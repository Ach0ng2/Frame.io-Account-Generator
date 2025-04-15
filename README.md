
# Frame.io Account Generator

This Python script automates the process of generating a fake email using [fakemail.net](https://www.fakemail.net/) and signing up for a Frame.io account. It uses Selenium to open a Chrome browser and interact with both webpages to fill out the sign-up form automatically. The browser remains open in case of errors for debugging purposes.

## Prerequisites

Before running the script, please ensure you have the following installed on your system:

- **Python 3.6+**
- **pip** (Python package installer)
- **Google Chrome**  
- **ChromeDriver**  
  Download ChromeDriver from [ChromeDriver - WebDriver for Chrome](https://chromedriver.chromium.org/downloads) and ensure that it matches the version of Google Chrome you have installed. Make sure the `chromedriver` executable is in your system's `PATH` or specify its path directly in the script if needed.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Install Python Dependencies:**

   A `requirements.txt` file is provided for your convenience. To install the necessary libraries, run:

   ```bash
   pip install -r requirements.txt
   ```

   The primary dependency is:
   - `selenium`

   You can create the `requirements.txt` with the following content if you haven't already:

   ```txt
   selenium>=4.0.0
   ```

## Running the Script

To run the script, execute the following command in your terminal:

```bash
python frameio_account_generator(1).py
```

When you run the script, it will perform these actions:

1. Open [fakemail.net](https://www.fakemail.net/) to retrieve a temporary email address.
2. Open a new browser tab and navigate to the Frame.io signup page.
3. Automatically fill the sign-up form with the fake email and a randomly generated name.
4. Enter the password and submit the signup form.
5. Switch back to the fakemail.net tab to check for the Frame.io confirmation email.

If any errors occur during the process, a detailed error message and stack trace will be printed in the terminal, and the Chrome browser window will remain open for debugging.

## Troubleshooting

- **ChromeDriver Issues:**  
  Ensure that you have downloaded the correct version of ChromeDriver that matches your installed version of Chrome. Confirm that ChromeDriver is accessible in your system's `PATH`.

- **Selenium Errors:**  
  Verify that the Selenium package is installed and up-to-date by running `pip show selenium` or updating it with `pip install --upgrade selenium`.

- **Script Errors:**  
  Refer to the console output for any error messages. The script outputs detailed information and retains the open browser for debugging if an error occurs.

## License

This project is licensed under the [MIT License](LICENSE).
