from app.knowledge.research_crawler import ResearchCrawler


def test_text_file_allowlist():
    assert ResearchCrawler._is_text_file("src/packet.cs")
    assert ResearchCrawler._is_text_file("README.md")
    assert not ResearchCrawler._is_text_file("client/game.exe")
    assert not ResearchCrawler._is_text_file("assets/image.png")


def test_title_extraction():
    assert ResearchCrawler._title("<title>NosTale Research</title><p>x</p>") == "NosTale Research"
