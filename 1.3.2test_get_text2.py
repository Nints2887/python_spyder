import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def fetch_page_content(url, base_domain):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 处理HTTP错误
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取小说内容（多个<p>标签）
        content_div = soup.find('div', id='dashu_text')
        if not content_div:
            print(f"警告：{url} 未找到内容区域")
            return None, None
        
        # 修复：先提取所有段落文本，再合并
        paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p')]
        text_content = '\n'.join(paragraphs)
        
        # 提取下一页链接
        next_url = None
        pagination = soup.find('div', id='pageurl')
        if pagination:
            next_page = pagination.find('a', string='下一页')
            if next_page:
                next_url = urljoin(base_domain, next_page['href'])
            else:
                print(f"警告：{url} 未找到下一页按钮")
        else:
            print(f"警告：{url} 未找到分页区域")
        
        return text_content, next_url
    
    except requests.exceptions.RequestException as e:
        print(f"请求错误：{e}")
        return None, None

def crawl_novel(start_url, base_domain):
    all_content = []
    current_url = start_url
    page_count = 0
    
    while current_url and page_count < 1000:
        content, next_url = fetch_page_content(current_url, base_domain)
        if content:
            all_content.append(content)
            print(f"已爬取第 {page_count+1} 页：{current_url}")
            page_count += 1
        current_url = next_url
        time.sleep(1)
    
    return '\n'.join(all_content)

if __name__ == "__main__":
    base_domain = "http://www.newxue.com"
    start_url = "http://www.newxue.com/xiaoshuo/138374796514750.html"
    
    print("开始爬取小说...")
    novel_text = crawl_novel(start_url, base_domain)
    
    with open("novel_content.txt", "w", encoding="utf-8") as f:
        f.write(novel_text)
    
    # 修复：先计算行数，再在f-string中使用
    line_count = len(novel_text.split('\n'))
    print(f"爬取完成，共 {line_count} 行内容，已保存到novel_content.txt")