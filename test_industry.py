import os
from agent.industry_agent import IndustryAgent


def test_supplychain_agent():
    # === 测试参数设置 ===
    test_data_dir = "./data/证券"  # 替换为你的测试用 JSON 报告目录
    industry_name = "证券"       # 行业名称（用于构造 prompt 和文件名）
    output_path = "./test_output/industry_report_test.json"  # 可自定义路径

    # 创建输出目录（如未存在）
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # === 初始化 Agent ===
    agent = IndustryAgent()

    # === 执行分析 ===
    report = agent.analyze_industry(
        industry_dir=test_data_dir,
        industry_name=industry_name,
        output_path=output_path
    )

    # === 测试检查 ===
    assert report is not None, "❌ 行业报告生成失败，返回值为 None"
    assert "llm_report" in report, "❌ 报告中未包含 LLM 生成内容"
    assert "industry_name" in report and report["industry_name"] == industry_name, "❌ 行业名称不匹配"
    assert os.path.exists(output_path), "❌ JSON 报告未写入输出路径"
    assert os.path.exists(output_path.replace(".json", ".txt")), "❌ TXT 文本摘要未写入"

    print("✅ 测试通过：SupplyChainAgent 正常运行，输出已生成")
    print("🔍 生成的行业分析报告路径：", output_path)

if __name__ == "__main__":
    test_supplychain_agent()
