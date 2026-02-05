#!/usr/bin/env python3
"""
Twitter 推文爬取脚本
使用 tweety-ns 库获取指定用户的推文，保存为 Markdown 格式
"""
import argparse
import json
import os
import sys
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

# 添加 trend-crawler 的虚拟环境
TREND_CRAWLER_PATH = Path.home() / "Documents" / "trend-crawler-master" / "trend-crawler"
# VENV_PATH = TREND_CRAWLER_PATH / "venv" / "lib" / "python3.13" / "site-packages"
# if VENV_PATH.exists():
#     sys.path.insert(0, str(VENV_PATH))

from tweety import Twitter
import yaml


# 频率限制配置
DEFAULT_MIN_INTERVAL = 5.0  # 最小请求间隔（秒）
DEFAULT_MAX_RETRIES = 3     # 最大重试次数

# 全局状态
_last_request_time = 0


def rate_limit_wait(min_interval: float = DEFAULT_MIN_INTERVAL):
    """频率限制等待"""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < min_interval:
        wait_time = min_interval - elapsed
        # 添加随机抖动，避免被检测
        jitter = random.uniform(0.5, 2.0)
        total_wait = wait_time + jitter
        print(f"⏳ 等待 {total_wait:.1f} 秒（频率限制）...")
        time.sleep(total_wait)
    _last_request_time = time.time()


class TwitterCrawler:
    """Twitter 推文爬取器"""
    
    def __init__(self, auth_token: Optional[str] = None, config_path: Optional[str] = None):
        """
        初始化爬取器
        
        Args:
            auth_token: Twitter auth_token，如果不提供则从配置文件读取
            config_path: 配置文件路径
        """
        self.auth_token = auth_token
        
        # 尝试从配置文件加载 auth_token
        if not self.auth_token and config_path:
            self.auth_token = self._load_auth_token(config_path)
        
        # 尝试从 trend-crawler 的配置加载
        if not self.auth_token:
            trend_config = TREND_CRAWLER_PATH / "config.yaml"
            if trend_config.exists():
                self.auth_token = self._load_auth_token(str(trend_config))
        
        # 创建 Twitter 实例
        self.app = Twitter("session")
        if self.auth_token:
            self.app.load_auth_token(self.auth_token)
            print("✅ 已加载 auth_token")
        else:
            print("⚠️  未配置 auth_token，使用访客模式（可能受限）")
    
    def _load_auth_token(self, config_path: str) -> Optional[str]:
        """从配置文件加载 auth_token"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('twitter_accounts', {}).get('auth_token')
        except Exception as e:
            print(f"⚠️  加载配置失败: {e}")
            return None
    
    def get_user_info(self, username: str) -> dict:
        """获取用户信息"""
        rate_limit_wait()
        try:
            user = self.app.get_user_info(username)
            return {
                'success': True,
                'name': user.name,
                'username': user.username,
                'followers': user.followers_count,
                'following': user.friends_count,
                'description': user.description or '',
                'profile_image': getattr(user, 'profile_image_url_https', ''),
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_tweets(self, username: str, limit: int = 10, pages: int = 1) -> list:
        """
        获取用户推文
        
        Args:
            username: Twitter 用户名
            limit: 获取推文数量
            pages: 获取页数（每页约20条，多页间会自动等待）
        
        Returns:
            推文列表
        """
        tweets_data = []
        
        rate_limit_wait()
        try:
            tweets = self.app.get_tweets(username, pages=pages)
            
            count = 0
            for tweet in tweets:
                if not hasattr(tweet, 'text'):
                    continue
                if count >= limit:
                    break
                count += 1
                
                # 获取媒体
                media_urls = []
                if hasattr(tweet, 'media') and tweet.media:
                    for m in tweet.media:
                        if hasattr(m, 'media_url_https') and m.media_url_https:
                            media_urls.append(m.media_url_https)
                
                # 获取互动数据
                replies = getattr(tweet, 'reply_counts', 0) or 0
                views = getattr(tweet, 'views', 0)
                if views == 'Unavailable':
                    views = 0
                views = int(views) if views else 0
                
                tweets_data.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': str(tweet.created_on),
                    'likes': tweet.likes,
                    'retweets': tweet.retweet_counts,
                    'replies': replies,
                    'views': views,
                    'url': f"https://twitter.com/{username}/status/{tweet.id}",
                    'media': media_urls,
                    'is_retweet': getattr(tweet, 'is_retweet', False) or False,
                    'is_quote': getattr(tweet, 'is_quoted', False) or False,
                    'is_reply': getattr(tweet, 'is_reply', False) or False,
                })
            
            print(f"✅ 获取 {len(tweets_data)} 条推文")
            return tweets_data
            
        except Exception as e:
            print(f"❌ 获取推文失败: {e}")
            return []
    
    def to_markdown(
        self,
        username: str,
        tweets: list,
        user_info: dict = None,
        include_fields: list = None,
        title: str = None
    ) -> str:
        """
        将推文转换为 Markdown 格式
        
        Args:
            username: 用户名
            tweets: 推文列表
            user_info: 用户信息
            include_fields: 包含的字段，默认全部
                可选: text, time, likes, retweets, replies, views, url, media
            title: 自定义标题
        
        Returns:
            Markdown 字符串
        """
        if include_fields is None:
            include_fields = ['text', 'time', 'likes', 'retweets', 'replies', 'url', 'media']
        
        lines = []
        
        # 标题
        if title:
            lines.append(f"# {title}")
        else:
            lines.append(f"# @{username} 的推文")
        
        lines.append("")
        lines.append(f"> 爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"> 推文数量: {len(tweets)}")
        lines.append("")
        
        # 用户信息
        if user_info and user_info.get('success'):
            lines.append("## 用户信息")
            lines.append("")
            lines.append(f"- **名称**: {user_info['name']}")
            lines.append(f"- **用户名**: @{user_info['username']}")
            lines.append(f"- **粉丝**: {user_info['followers']:,}")
            lines.append(f"- **关注**: {user_info['following']:,}")
            if user_info.get('description'):
                lines.append(f"- **简介**: {user_info['description'][:200]}")
            lines.append("")
        
        # 推文列表
        lines.append("## 推文列表")
        lines.append("")
        
        for i, tweet in enumerate(tweets, 1):
            lines.append(f"### {i}. 推文")
            lines.append("")
            
            if 'time' in include_fields:
                lines.append(f"**时间**: {tweet['created_at']}")
                lines.append("")
            
            if 'text' in include_fields:
                # 处理推文文本，保留换行
                text = tweet['text'].replace('\n', '\n> ')
                lines.append(f"> {text}")
                lines.append("")
            
            # 互动数据
            stats = []
            if 'likes' in include_fields:
                stats.append(f"❤️ {tweet['likes']:,}")
            if 'retweets' in include_fields:
                stats.append(f"🔁 {tweet['retweets']:,}")
            if 'replies' in include_fields:
                stats.append(f"💬 {tweet['replies']:,}")
            if 'views' in include_fields and tweet['views']:
                stats.append(f"👁 {tweet['views']:,}")
            
            if stats:
                lines.append(f"**互动**: {' | '.join(stats)}")
                lines.append("")
            
            if 'url' in include_fields:
                lines.append(f"**链接**: [{tweet['url']}]({tweet['url']})")
                lines.append("")
            
            if 'media' in include_fields and tweet['media']:
                lines.append("**媒体**:")
                for media_url in tweet['media']:
                    lines.append(f"- ![]({media_url})")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return '\n'.join(lines)
    
    def save_markdown(self, content: str, output_path: str):
        """保存 Markdown 文件"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 已保存到: {output_path}")
    
    def save_json(self, tweets: list, user_info: dict, output_path: str):
        """保存 JSON 文件"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'user': user_info,
            'tweets': tweets,
            'fetched_at': datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='爬取 Twitter 用户推文')
    parser.add_argument('username', help='Twitter 用户名（不含@）')
    parser.add_argument('-n', '--limit', type=int, default=10, help='获取推文数量（默认10）')
    parser.add_argument('-p', '--pages', type=int, default=1, help='获取页数（默认1，每页约20条）')
    parser.add_argument('-o', '--output', help='输出文件路径（默认 outputs/{username}.md）')
    parser.add_argument('--json', action='store_true', help='同时输出 JSON 格式')
    parser.add_argument('--interval', type=float, default=5.0, help='请求间隔秒数（默认5）')
    parser.add_argument('--no-user-info', action='store_true', help='不获取用户信息')
    parser.add_argument('--title', help='自定义 Markdown 标题')
    parser.add_argument('--fields', help='包含的字段，逗号分隔（text,time,likes,retweets,replies,views,url,media）')
    parser.add_argument('--auth-token', help='Twitter auth_token')
    
    args = parser.parse_args()
    
    # 设置频率限制
    global DEFAULT_MIN_INTERVAL
    DEFAULT_MIN_INTERVAL = args.interval
    
    # 创建爬取器
    crawler = TwitterCrawler(auth_token=args.auth_token)
    
    # 获取用户名（去掉@）
    username = args.username.lstrip('@')
    
    # 根据 limit 自动计算需要的页数
    pages = args.pages
    if args.limit > 20 and pages == 1:
        pages = (args.limit // 20) + 1
        print(f"📢 需要 {args.limit} 条推文，自动调整为 {pages} 页")
    
    print(f"\n📋 获取 @{username} 的推文...")
    print(f"   数量: {args.limit}，页数: {pages}，间隔: {args.interval}秒")
    
    # 获取用户信息
    user_info = None
    if not args.no_user_info:
        user_info = crawler.get_user_info(username)
        if user_info.get('success'):
            print(f"   用户: {user_info['name']} ({user_info['followers']:,} 粉丝)")
    
    # 获取推文
    tweets = crawler.get_tweets(username, limit=args.limit, pages=pages)
    
    if not tweets:
        print("❌ 未获取到推文")
        sys.exit(1)
    
    # 解析字段
    include_fields = None
    if args.fields:
        include_fields = [f.strip() for f in args.fields.split(',')]
    
    # 生成 Markdown
    markdown = crawler.to_markdown(
        username=username,
        tweets=tweets,
        user_info=user_info,
        include_fields=include_fields,
        title=args.title
    )
    
    # 确定输出路径
    output_dir = Path(__file__).parent.parent / 'outputs'
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = output_dir / f"{username}.md"
    
    # 保存文件
    crawler.save_markdown(markdown, output_path)
    
    # 可选：保存 JSON
    if args.json:
        json_path = output_path.with_suffix('.json')
        crawler.save_json(tweets, user_info, json_path)
    
    print(f"\n✅ 完成！")


if __name__ == '__main__':
    main()
