"""
Property-based tests for security features
"""
import pytest
from hypothesis import given, strategies as st, assume
import re
from src.utils.security import ContentSanitizer


class TestExternalLinkHandling:
    """Property-based tests for external link processing"""
    
    @given(
        external_url=st.one_of(
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=5, max_size=20).map(lambda x: f"https://example.com/{x}"),
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=5, max_size=20).map(lambda x: f"http://external-site.org/{x}"),
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=5, max_size=20).map(lambda x: f"https://different-domain.net/{x}")
        ),
        link_text=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=1, max_size=50).filter(lambda x: '<' not in x and '>' not in x and x.strip())
    )
    def test_external_links_get_security_attributes(self, external_url, link_text):
        """
        **Feature: blog-system, Property 12: External link handling**
        *For any* external links within blog post content, the rendered HTML should include 
        target="_blank" attributes to open links in new tabs
        **Validates: Requirements 5.5**
        """
        # Create HTML content with an external link
        html_content = f'<p>Check out this <a href="{external_url}">{link_text}</a> for more info.</p>'
        
        # Process the content
        processed_content = ContentSanitizer.sanitize_html(html_content)
        
        # Verify that external links have security attributes
        # Should have target="_blank" for opening in new tab
        assert 'target="_blank"' in processed_content, f"External link should have target='_blank': {processed_content}"
        
        # Should have rel="noopener noreferrer" for security
        assert 'rel="noopener noreferrer"' in processed_content, f"External link should have security rel attributes: {processed_content}"
        
        # Should preserve the original URL and link text
        assert external_url in processed_content, f"Original URL should be preserved: {processed_content}"
        assert link_text in processed_content, f"Link text should be preserved: {processed_content}"
    
    @given(
        internal_path=st.one_of(
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=20).map(lambda x: f"/{x}"),
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=20).map(lambda x: f"/blog/{x}"),
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=20).map(lambda x: f"/admin/{x}")
        ),
        link_text=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=1, max_size=50).filter(lambda x: '<' not in x and '>' not in x and x.strip())
    )
    def test_internal_links_remain_unchanged(self, internal_path, link_text):
        """
        **Feature: blog-system, Property 12: External link handling**
        Internal links should not be modified with external link attributes
        **Validates: Requirements 5.5**
        """
        # Create HTML content with an internal link
        html_content = f'<p>Go to <a href="{internal_path}">{link_text}</a> page.</p>'
        
        # Process the content
        processed_content = ContentSanitizer.sanitize_html(html_content)
        
        # Internal links should NOT have target="_blank"
        # Extract the specific link to check
        link_pattern = rf'<a[^>]*href="{re.escape(internal_path)}"[^>]*>'
        link_match = re.search(link_pattern, processed_content)
        
        if link_match:
            link_tag = link_match.group(0)
            # Internal links should not have target="_blank" added
            assert 'target="_blank"' not in link_tag, f"Internal link should not have target='_blank': {link_tag}"
        
        # Should preserve the original path and link text
        assert internal_path in processed_content, f"Internal path should be preserved: {processed_content}"
        assert link_text in processed_content, f"Link text should be preserved: {processed_content}"
    
    @given(
        mixed_content=st.lists(
            st.one_of(
                st.tuples(
                    st.just("external"),
                    st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=5, max_size=15).map(lambda x: f"https://external.com/{x}"),
                    st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=1, max_size=20).filter(lambda x: '<' not in x and '>' not in x and x.strip())
                ),
                st.tuples(
                    st.just("internal"),
                    st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=15).map(lambda x: f"/{x}"),
                    st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=1, max_size=20).filter(lambda x: '<' not in x and '>' not in x and x.strip())
                )
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_mixed_links_processed_correctly(self, mixed_content):
        """
        **Feature: blog-system, Property 12: External link handling**
        Content with both internal and external links should be processed correctly
        **Validates: Requirements 5.5**
        """
        # Build HTML content with mixed links
        html_parts = []
        expected_external_count = 0
        expected_internal_count = 0
        
        for link_type, url, text in mixed_content:
            html_parts.append(f'<a href="{url}">{text}</a>')
            if link_type == "external":
                expected_external_count += 1
            else:
                expected_internal_count += 1
        
        html_content = f'<p>{" and ".join(html_parts)}</p>'
        
        # Process the content
        processed_content = ContentSanitizer.sanitize_html(html_content)
        
        # Count external links with security attributes
        external_secure_links = len(re.findall(r'<a[^>]*target="_blank"[^>]*>', processed_content))
        
        # All external links should have security attributes
        assert external_secure_links == expected_external_count, \
            f"Expected {expected_external_count} external links with security attributes, got {external_secure_links}"
        
        # Verify all original URLs and texts are preserved
        for link_type, url, text in mixed_content:
            assert url in processed_content, f"URL {url} should be preserved"
            assert text in processed_content, f"Text {text} should be preserved"
    
    def test_malformed_links_handled_safely(self):
        """
        **Feature: blog-system, Property 12: External link handling**
        Malformed or edge case links should be handled safely without breaking
        **Validates: Requirements 5.5**
        """
        test_cases = [
            '<a href="">Empty href</a>',
            '<a href="javascript:alert(1)">XSS attempt</a>',
            '<a href="data:text/html,<script>alert(1)</script>">Data URL</a>',
            '<a>No href attribute</a>',
            '<a href="https://example.com" onclick="alert(1)">With onclick</a>'
        ]
        
        for html_content in test_cases:
            # Should not raise an exception
            processed_content = ContentSanitizer.sanitize_html(html_content)
            
            # Should not contain dangerous protocols or scripts
            assert 'javascript:' not in processed_content.lower()
            # Check that onclick attribute is not present (not in link text)
            assert 'onclick=' not in processed_content.lower()
            assert '<script>' not in processed_content.lower()