#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動生成股票研究對比摘要腳本

此腳本會掃描指定股票的研究報告，提取關鍵資訊並生成對比摘要。
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse


class ResearchReport:
    """研究報告解析類"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.version = self._extract_version(file_path.name)
        self.date = self._extract_date(file_path.name)
        self.content = self._read_content()
        self.sections = self._parse_sections()
    
    def _extract_version(self, filename: str) -> Optional[str]:
        """從檔名提取版本號"""
        match = re.search(r'v(\d+)', filename)
        return match.group(1) if match else None
    
    def _extract_date(self, filename: str) -> Optional[str]:
        """從檔名提取日期"""
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        return match.group(1) if match else None
    
    def _read_content(self) -> str:
        """讀取報告內容"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"讀取檔案失敗 {self.file_path}: {e}")
            return ""
    
    def _parse_sections(self) -> Dict[str, str]:
        """解析報告章節"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in self.content.split('\n'):
            # 檢測二級標題（##）
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # 最後一個章節
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def get_pricing_prediction(self) -> Dict[str, str]:
        """提取定價預測資訊"""
        result = {
            'target_price': None,
            'current_price': None,
            'direction': None,
            'time_range': None
        }
        
        pricing_section = self.sections.get('定價預測', '')
        if not pricing_section:
            return result
        
        # 提取目標價格
        target_match = re.search(r'目標價格[：:]\s*([\d,]+\.?\d*)\s*([^\s\n]*)', pricing_section)
        if target_match:
            result['target_price'] = f"{target_match.group(1)} {target_match.group(2).strip()}"
        
        # 提取當前價格
        current_match = re.search(r'當前價格[：:]\s*([\d,]+\.?\d*)\s*([^\s\n]*)', pricing_section)
        if current_match:
            result['current_price'] = f"{current_match.group(1)} {current_match.group(2).strip()}"
        
        # 提取預測方向
        direction_match = re.search(r'預測方向[：:]\s*([看漲看跌中性]+)', pricing_section)
        if direction_match:
            result['direction'] = direction_match.group(1)
        
        # 提取時間範圍
        time_match = re.search(r'時間範圍[：:]\s*([^\n]+)', pricing_section)
        if time_match:
            result['time_range'] = time_match.group(1).strip()
        
        return result
    
    def get_key_points(self) -> List[str]:
        """提取關鍵觀點"""
        points = []
        
        # 從執行摘要提取
        summary = self.sections.get('執行摘要', '')
        if summary:
            # 提取列表項
            for line in summary.split('\n'):
                if line.strip().startswith('- ') or line.strip().startswith('* '):
                    points.append(line.strip()[2:].strip())
        
        return points[:5]  # 最多返回5個關鍵點
    
    def get_risk_assessment(self) -> str:
        """提取風險評估"""
        risk_section = self.sections.get('風險評估', '')
        if not risk_section:
            return ""
        
        # 提取風險等級
        risk_match = re.search(r'整體風險等級[：:]\s*([低中高]+)', risk_section)
        if risk_match:
            return risk_match.group(1)
        
        return ""


def find_research_reports(stock_dir: Path) -> List[ResearchReport]:
    """找出所有研究報告"""
    research_dir = stock_dir / 'research'
    if not research_dir.exists():
        return []
    
    reports = []
    for file_path in sorted(research_dir.glob('v*.md')):
        try:
            report = ResearchReport(file_path)
            if report.version and report.date:
                reports.append(report)
        except Exception as e:
            print(f"解析報告失敗 {file_path}: {e}")
    
    # 按版本號排序
    reports.sort(key=lambda x: int(x.version) if x.version else 0)
    return reports


def calculate_price_change(price1: Optional[str], price2: Optional[str]) -> Optional[str]:
    """計算價格變化"""
    if not price1 or not price2:
        return None
    
    # 提取數字
    num1_match = re.search(r'([\d,]+\.?\d*)', price1)
    num2_match = re.search(r'([\d,]+\.?\d*)', price2)
    
    if not num1_match or not num2_match:
        return None
    
    try:
        val1 = float(num1_match.group(1).replace(',', ''))
        val2 = float(num2_match.group(1).replace(',', ''))
        
        if val1 == 0:
            return None
        
        change = ((val2 - val1) / val1) * 100
        sign = '+' if change > 0 else ''
        return f"{sign}{change:.2f}%"
    except:
        return None


def generate_summary(stock_code: str, stock_dir: Path) -> str:
    """生成對比摘要"""
    reports = find_research_reports(stock_dir)
    
    if not reports:
        return f"# {stock_code} 研究對比摘要\n\n尚未有研究報告。\n"
    
    # 提取股票名稱（從第一個報告的標題）
    stock_name = ""
    if reports:
        title_match = re.search(r'#\s*[\w]+\s+([^\s]+)', reports[0].content)
        if title_match:
            stock_name = title_match.group(1)
    
    lines = []
    lines.append(f"# {stock_code} {stock_name} 研究對比摘要")
    lines.append("")
    lines.append(f"> **生成時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"> **研究報告數量**：{len(reports)} 份")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 價格預測變化表
    lines.append("## 價格預測變化")
    lines.append("")
    lines.append("| 版本 | 研究日期 | 目標價格 | 當前價格 | 預測方向 | 時間範圍 | 變化幅度 |")
    lines.append("|------|---------|---------|---------|---------|---------|---------|")
    
    prev_price = None
    for i, report in enumerate(reports):
        pricing = report.get_pricing_prediction()
        target_price = pricing.get('target_price', '-')
        current_price = pricing.get('current_price', '-')
        direction = pricing.get('direction', '-')
        time_range = pricing.get('time_range', '-')
        
        # 計算變化幅度
        change = '-'
        if i > 0 and prev_price and target_price != '-':
            change = calculate_price_change(prev_price, target_price) or '-'
        
        lines.append(f"| v{report.version:0>3} | {report.date} | {target_price} | {current_price} | {direction} | {time_range} | {change} |")
        
        if target_price != '-':
            prev_price = target_price
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 關鍵觀點演變
    lines.append("## 關鍵觀點演變")
    lines.append("")
    
    for report in reports:
        lines.append(f"### v{report.version:0>3} - {report.date}")
        lines.append("")
        key_points = report.get_key_points()
        if key_points:
            for point in key_points:
                lines.append(f"- {point}")
        else:
            lines.append("- （未提取到關鍵觀點）")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # 風險評估變化
    lines.append("## 風險評估變化")
    lines.append("")
    lines.append("| 版本 | 研究日期 | 風險等級 |")
    lines.append("|------|---------|---------|")
    
    for report in reports:
        risk = report.get_risk_assessment() or '-'
        lines.append(f"| v{report.version:0>3} | {report.date} | {risk} |")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 趨勢分析
    lines.append("## 趨勢分析")
    lines.append("")
    
    if len(reports) >= 2:
        first_pricing = reports[0].get_pricing_prediction()
        last_pricing = reports[-1].get_pricing_prediction()
        
        first_dir = first_pricing.get('direction', '')
        last_dir = last_pricing.get('direction', '')
        
        if first_dir and last_dir:
            if first_dir != last_dir:
                lines.append(f"**預測方向變化**：從「{first_dir}」轉為「{last_dir}」")
            else:
                lines.append(f"**預測方向**：維持「{last_dir}」")
            lines.append("")
        
        first_price = first_pricing.get('target_price', '')
        last_price = last_pricing.get('target_price', '')
        
        if first_price and last_price:
            change = calculate_price_change(first_price, last_price)
            if change:
                lines.append(f"**目標價格變化**：從 {first_price} 到 {last_price}（{change}）")
                lines.append("")
    else:
        lines.append("需要至少兩份報告才能進行趨勢分析。")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("*此摘要由自動化腳本生成，如有疑問請查閱原始研究報告。*")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='生成股票研究對比摘要')
    parser.add_argument('stock_code', help='股票代碼（如 2330、AAPL）')
    parser.add_argument('--stocks-dir', default='stocks', help='股票目錄路徑（預設：stocks）')
    
    args = parser.parse_args()
    
    stocks_dir = Path(args.stocks_dir)
    stock_dir = stocks_dir / args.stock_code
    
    if not stock_dir.exists():
        print(f"錯誤：找不到股票目錄 {stock_dir}")
        return 1
    
    summary_content = generate_summary(args.stock_code, stock_dir)
    summary_path = stock_dir / 'summary.md'
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"對比摘要已生成：{summary_path}")
    return 0


if __name__ == '__main__':
    exit(main())

