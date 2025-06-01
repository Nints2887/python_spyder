import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_page_content(url, base_domain):
    """获取页面内容和下一页链接"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, None
    
    response.encoding = response.apparent_encoding  # 自动检测编码
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取小说内容（根据网页结构，内容在#dashu_text div内）
    content_div = soup.find('div', id='dashu_text')
    if not content_div:
        return None, None
    text_content = content_div.get_text(separator='\n', strip=True)
    
    # 提取下一页链接（查找"下一页"按钮）
    next_page_link = soup.find('div', id='pageurl').find('a', string='下一页')
    next_url = urljoin(base_domain, next_page_link['href']) if next_page_link else None
    
    return text_content, next_url

def crawl_novel(start_url, base_domain):
    """爬取整本小说"""
    all_content = []
    current_url = start_url
    
    while current_url:
        content, next_url = fetch_page_content(current_url, base_domain)
        if content:
            all_content.append(content)
            print(f"已爬取：{current_url}")
        current_url = next_url
    
    return '\n'.join(all_content)

if __name__ == "__main__":
    base_domain = "http://www.newxue.com"
    start_url = "http://www.newxue.com/xiaoshuo/138374796514750.html"  # 第一页URL
    
    novel_text = crawl_novel(start_url, base_domain)
    
    # 保存到文件
    with open("novel_content.txt", "w", encoding="utf-8") as f:
        f.write(novel_text)
    
    print("爬取完成，内容已保存到novel_content.txt")
