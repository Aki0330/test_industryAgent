import os
import json
from typing import List, Dict
from collections import Counter, defaultdict


class IndustryReportLoader:

    def load_industry_reports(self, folder_path: str) -> List[Dict]:
        """
        加载目录下所有JSON格式的公司报告
        """
        reports = []
        for fname in os.listdir(folder_path):
            if fname.endswith(".json"):
                fpath = os.path.join(folder_path, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        reports.append(report)
                except Exception as e:
                    print(f"[!] 读取文件失败: {fpath}, 错误: {e}")
        return reports

    def aggregate_industry_data(self, reports: List[Dict]) -> Dict:
        """
        聚合行业级信息，用于构造 prompt 和行业总结
        """
        region_counter = Counter()
        subindustry_counter = Counter()
        keywords_counter = Counter()
        risks_set = set()
        recent_events = []
        supply_chain = defaultdict(set)
        top_companies = []

        for report in reports:
            metadata = report.get("analysis_metadata", {})
            basic_info = metadata.get("company_basic_info", {})
            quantum = metadata.get("quantum_metadata", {})

            name = basic_info.get("name", "未知企业")
            industry = basic_info.get("industry", "未知行业")
            location = basic_info.get("hq_location", "未知地点")

            region_counter[location] += 1
            subindustry_counter[industry] += 1
            top_companies.append(name)

            # 抽取风险关键词
            quantum_report = report.get("quantum_enhanced_analysis", "")
            if "风险" in quantum_report:
                for line in quantum_report.splitlines():
                    if "风险" in line and len(line.strip()) > 4:
                        risks_set.add(line.strip())

            # 提取未来展望关键词
            for kw_line in quantum_report.splitlines():
                if "未来" in kw_line or "趋势" in kw_line or "前景" in kw_line:
                    keywords_counter.update(kw_line.replace("：", ":").split(":")[-1].strip().split())

            # 抽取事件线索
            tavily_report = report.get("tavily_report", "")
            if "事件" in tavily_report or "合作" in tavily_report or "融资" in tavily_report:
                recent_events.append(tavily_report)

            # 上下游（如果有）
            sc = report.get("supply_chain", {})
            for u in sc.get("upstream", []):
                supply_chain["upstream"].add(u)
            for d in sc.get("downstream", []):
                supply_chain["downstream"].add(d)

        return {
            "company_count": len(reports),
            "regions": list(region_counter.most_common(5)),
            "sub_industries": list(subindustry_counter.most_common(5)),
            "top_companies": top_companies[:10],
            "recent_events": recent_events[:5],
            "supply_chain_brief": {
                "upstream": list(supply_chain["upstream"])[:5],
                "downstream": list(supply_chain["downstream"])[:5]
            },
            "risks": list(risks_set)[:10],
            "tech_trends": list(keywords_counter.most_common(5)),
            "future_outlook": [kw for kw, _ in keywords_counter.most_common(10)],
        }

    def save_industry_report(self, report: Dict, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    def save_industry_txt(self, report: Dict, path: str):
        llm_text = report.get("llm_report", "暂无生成内容")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"【行业分析报告】\n行业名称：{report.get('industry_name')}\n\n")
            f.write(llm_text)
