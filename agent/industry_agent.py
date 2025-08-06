import os
from tools.IndustryReport_loader import IndustryReportLoader  # 需要你实现该类
from llm.deepseek_llm import DeepSeekLLM


class IndustryAgent:
    def __init__(self):
        self.loader = IndustryReportLoader()
        self.llm = DeepSeekLLM()

    def analyze_industry(self, industry_dir, industry_name, output_path=None):
        """
        分析某一行业，输出结构化行业分析报告
        :param industry_dir: 包含多个公司 JSON 分析报告的文件夹路径
        :param industry_name: 行业名称
        :param output_path: 输出报告路径（可选）
        :return: 行业分析报告（dict 格式）
        """

        # 1. 加载行业公司报告
        company_reports = self.loader.load_industry_reports(industry_dir)
        if not company_reports:
            print(f"[!] 未在路径 {industry_dir} 下找到任何 JSON 报告")
            return None

        print(f"已加载 {len(company_reports)} 份公司报告")

        # 2. 提取行业基本信息（由 Loader 提供聚合字段，如地域分布、主营业务、重大事件等）
        industry_summary = self.loader.aggregate_industry_data(company_reports)

        # 3. 构造 prompt，生成行业分析文本（五大模块）
        prompt = self._generate_industry_prompt(industry_name, industry_summary)
        llm_report = self.llm.chat(prompt)

        # 4. 组装最终报告结构
        industry_report = {
            "industry_name": industry_name,
            "companies_count": len(company_reports),
            "aggregated_data": industry_summary,
            "llm_report": llm_report
        }

        # 5. 保存 JSON 格式报告
        if output_path is None:
            output_path = f"industry_report_{industry_name.replace(' ', '_')}.json"
        self.loader.save_industry_report(industry_report, output_path)
        print(f"行业分析报告已保存至: {output_path}")

        # 6. 输出为 .txt 文本摘要（结构化）
        txt_path = os.path.splitext(output_path)[0] + ".txt"
        self.loader.save_industry_txt(industry_report, txt_path)

        return industry_report
#prompt部分
    def _generate_industry_prompt(self, industry_name, summary):
        """
        组织 Prompt，用于 LLM 生成结构化行业分析报告
        """
        return f"""
请根据以下原始行业数据，撰写一份全面的行业分析报告，面向投资者，输出框架如下：
1. 行业整体概况
2. 行业近期新闻
3. 地域间关联分析
4. 预测与风险分析
5. 总结与建议

行业名称：{industry_name}
公司数量：{summary.get("company_count")}
主要地区分布：{summary.get("regions")}
主要细分领域：{summary.get("sub_industries")}
核心企业：{summary.get("top_companies")}
近期行业事件：{summary.get("recent_events")}
上下游情况简要：{summary.get("supply_chain_brief")}
风险因素与挑战：{summary.get("risks")}
创新趋势与技术投入：{summary.get("tech_trends")}
未来市场前景关键词：{summary.get("future_outlook")}
        """
