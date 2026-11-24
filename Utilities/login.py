import asyncio
from playwright.async_api import async_playwright

# Folder where session will be saved
USER_DATA_DIR = r"C:/playwright-new-chrome"

async def main():
    async with async_playwright() as pw:
        print("🚀 Opening Chrome...")

        context = await pw.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            headless=False,
            args=[
                "--start-maximized",
                "--no-first-run",
                "--no-default-browser-check"
            ],
            no_viewport=True
        )

        # ✅ Just open a blank new tab
        await context.new_page()

        print("✅ Chrome opened.")
        print("👉 Do your login manually.")
        print("👉 Then CLOSE the browser yourself.")

        # ✅ Keep script alive until browser is closed
        
        print("⏳ You have 10 minutes to finish setup...")
        await asyncio.sleep(600)

        print("Thank you for setting up your profile!!!")


if __name__ == "__main__":
    asyncio.run(main())