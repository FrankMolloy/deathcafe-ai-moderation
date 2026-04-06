from getpass import getpass
from urllib.parse import urljoin

from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright

from moderation.models import Post
from moderation.services.moderation_pipeline import run_moderation_pipeline


ADMIN_URL = "https://deathcafe.com/admin/deathcafe/blogpost/?state__exact=pending"
LOGIN_URL = "https://deathcafe.com/admin/login/"


class Command(BaseCommand):
    help = "Import pending posts from external Django admin"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=5,
            help="Maximum number of posts to import",
        )

    def handle(self, *args, **options):
        username = input("Admin username: ").strip()
        password = getpass("Admin password: ")
        limit = options["limit"]

        scraped_posts = []

        # -----------------------------
        # Step 1: Scrape with Playwright
        # -----------------------------
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            try:
                # Login
                page.goto(LOGIN_URL, wait_until="networkidle")
                page.fill('input[name="username"]', username)
                page.fill('input[name="password"]', password)
                page.click('input[type="submit"]')
                page.wait_for_load_state("networkidle")

                # Go to filtered pending posts page
                page.goto(ADMIN_URL, wait_until="networkidle")

                print(f"Final URL after login: {page.url}")
                print(f"Page title: {page.title()}")
                print("Logged in. Scraping posts...")

                rows = page.query_selector_all("#result_list tbody tr")
                print(f"Found {len(rows)} rows in result table")

                post_links = []

                for row in rows:
                    link = row.query_selector("th a")
                    if not link:
                        continue

                    href = link.get_attribute("href")
                    if not href:
                        continue

                    full_url = urljoin(page.url, href)
                    post_links.append(full_url)

                print(f"Found {len(post_links)} posts")

                for link in post_links[:limit]:
                    print(f"\nProcessing: {link}")

                    page.goto(link, wait_until="networkidle")

                    title_el = page.query_selector(".field-title input")
                    title = title_el.input_value().strip() if title_el else ""

                    body_el = page.query_selector(".field-post textarea")
                    body = body_el.input_value().strip() if body_el else ""

                    state_el = page.query_selector(".field-state select")
                    state = state_el.input_value().strip() if state_el else ""

                    image_link_el = page.query_selector(".field-image1 a")
                    image_url = (
                        urljoin(page.url, image_link_el.get_attribute("href"))
                        if image_link_el and image_link_el.get_attribute("href")
                        else ""
                    )

                    print(f"Title: {title}")
                    print(f"State: {state}")
                    print(f"Image present: {'yes' if image_url else 'no'}")

                    if not title or not body:
                        print("Skipping: missing title or body")
                        continue

                    scraped_posts.append(
                        {
                            "title": title,
                            "body": body,
                            "state": state,
                            "source_url": link,
                            "image_url": image_url,
                        }
                    )

            finally:
                browser.close()

        print(f"\nFinished scraping. {len(scraped_posts)} posts collected.")

        # --------------------------------------
        # Step 2: Save to Django after scraping
        # --------------------------------------
        for item in scraped_posts:
            print(f"\nSaving: {item['title']}")

            post, created = Post.objects.get_or_create(
                title=item["title"],
                body=item["body"],
            )

            if created:
                print("Created new post in moderation system")
            else:
                print("Post already exists in moderation system")

            run_moderation_pipeline(post, apply_auto_actions=False)
            print("Moderation completed")

        print("\nDone.")