import csv
import os
import sys

from wikiscraper import WikiScraper

HTML_TEST_FILE = "test_team_rocket.html"
TEST_HTML_CONTENT = """
<!DOCTYPE html>
<html>
<body>
    <div id="mw-content-text">
        <p>Team Rocket is a villainous team in pursuit of evil and the exploitation of Pokémon. 
        The organization is based in the Kanto and Johto regions, with a small outpost in the Sevii Islands.</p>
        <p>Another paragraph</p>
        
        <h2>Test table</h2>
        <table>
            <tbody>
                <tr>
                    <th>Stat name</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Strength</td>
                    <td>95</td>
                </tr>
                <tr>
                    <td>Speed</td>
                    <td>80</td>
                </tr>
            <tbody>
        </table>
        <a href="/wiki/Another_Page">Another page</a>
    </div>
</body>
</html>
"""

def setup_test_file():
    with open(HTML_TEST_FILE, "w") as f:
        f.write(TEST_HTML_CONTENT)

def cleanup_test_file():
    if os.path.exists(HTML_TEST_FILE):
        os.remove(HTML_TEST_FILE)

def check_summary(summary, expected_start, expected_end):
    return summary and summary.startswith(expected_start) and summary.endswith(expected_end)

def test_summary(wikiscraper):
    summary = wikiscraper.get_summary()
    if check_summary(summary, "Team Rocket", "outpost in the Sevii Islands."):
        print("Summary test passed!")
    else:
        print("Summary test failed!")
        sys.exit(1)

def test_table(wikiscraper):
    print("--------------")
    print("Table summary:")
    table = wikiscraper.get_table(1)
    print("--------------")
    CSV_NAME = "Team Rocket.csv"
    if not os.path.exists(CSV_NAME):
        raise AssertionError(f"CSV file {CSV_NAME} does not exist!")

    with open(CSV_NAME, "r", newline='') as f:
        reader = list(csv.reader(f))

        assert len(reader) == 3, f"Expected 3 rows in CSV file, but got {len(reader)}"
        assert reader[0] == ["", "Stat name", "Value"], "Header is incorrect"
        assert reader[1] == ["0", "Strength", "95"], "First row is incorrect"
        assert reader[2] == ["1", 'Speed', "80"], "Second row is incorrect"



def run_integration_test():
    setup_test_file()
    try:
        wikiscraper = WikiScraper("Team Rocket", local_html_file=HTML_TEST_FILE)

        test_summary(wikiscraper)
        test_table(wikiscraper)
        print("Table test passed!")

        print("All tests passed!")
    except Exception as e:
        print(f"Test failed with exception {e}")
        sys.exit(1)
    finally:
        cleanup_test_file()


if __name__ == "__main__":
    run_integration_test()