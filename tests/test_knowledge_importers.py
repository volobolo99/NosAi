from app.knowledge.importers.web import WebImporter


def test_html_to_text_strips_scripts_and_tags():
    text = WebImporter._html_to_text('<html><title>Bug</title><script>alert(1)</script><p>Hello&nbsp;world</p></html>')
    assert 'alert' not in text
    assert 'Hello world' in text
