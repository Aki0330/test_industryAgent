import streamlit as st
import pandas as pd
from agent.supply_chain_agent import SupplyChainAgent
from agent.regional_agent import RegionalAgent
from agent.industry_agent import IndustryAgent  # 确保路径正确
import tempfile
import os

st.set_page_config(page_title="行业智能分析", layout="wide")

st.title("行业智能分析助手")

# Tab切换：行业分析/地区分析
#tabs = st.tabs(["供应链分析", "地区分析"])
tabs = st.tabs(["供应链分析", "地区分析", "行业报告分析"])

# ========== 行业分析 Tab ==========
with tabs[0]:
    st.write("请上传包含企业因子和关联权重的CSV文件，系统将自动进行供应链&上下游趋势分析和预测。")
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"], key="industry_csv")
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        df = pd.read_csv(tmp_path)
        st.subheader("数据预览")
        st.dataframe(df)
        st.subheader("供应链分析报告")
        with st.spinner("正在分析，请稍候..."):
            agent = SupplyChainAgent()
            report, graph_img_path = agent.analyze(tmp_path)
        st.success("分析完成！")
        st.markdown(f"```\n{report}\n```")
        # 可选：展示行业关系图
        # st.subheader("企业关系图可视化")
        # st.image(graph_img_path, caption="行业企业关系图")
    else:
        st.info("请先上传CSV文件。")

# ========== 地区分析 Tab ==========
with tabs[1]:
    st.write("请上传同一地区的企业json报告文件（可多选），并输入地区名称，系统将自动进行地区级企业网络与集群分析。")
    uploaded_jsons = st.file_uploader("上传企业json报告（可多选）", type=["json"], accept_multiple_files=True, key="region_jsons")
    region_name = st.text_input("请输入地区名称（如：中国，北京市）", value="中国，北京市")
    if uploaded_jsons and region_name:
        # 将上传的json文件保存到临时目录
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_paths = []
            for file in uploaded_jsons:
                file_path = os.path.join(tmp_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())
                file_paths.append(file_path)
            st.write(f"已上传 {len(file_paths)} 份企业json报告")
            # 调用RegionalAgent分析
            with st.spinner("正在进行地区分析，请稍候..."):
                agent = RegionalAgent()
                # 直接传递临时目录
                report = agent.analyze_region(tmp_dir, region_name)
            if report:
                st.success("分析完成！")
                st.subheader("地区分析主要结论")
                st.markdown(f"**公司数量：** {report.get('companies_count', 0)}")
                st.markdown(f"**产业分布：** {report.get('industry_distribution', {})}")
                st.markdown(f"**产业集群强度：** {report.get('regional_insights', {}).get('economic_cluster_strength', {}).get('strength_level', '未知')}")
                st.markdown(f"**创新潜力：** {report.get('regional_insights', {}).get('innovation_potential', {}).get('potential_level', '未知')}")
                st.markdown(f"**协同分数：** {report.get('network_analysis', {}).get('synergy_score', '无')}")
                st.markdown(f"**枢纽企业：** {report.get('network_analysis', {}).get('hub_companies', [])}")
                st.markdown(f"**投资建议：** {report.get('investment_recommendations', {}).get('recommendation_level', '未知')}")
                
                # 展示LLM生成的智能分析报告
                if 'llm_report' in report:
                    st.subheader("AI智能分析报告")
                    st.markdown(report['llm_report'])
                
                # 展示网络图
                graph_img = report.get('network_analysis', {}).get('graph_image', None)
                if graph_img and os.path.exists(graph_img):
                    st.subheader("企业网络关系图（精简版）")
                    st.image(graph_img, caption="地区企业关系网络")
                # 提供txt报告下载
                txt_path = f"regional_report_{region_name.replace('，','_')}.txt"
                if os.path.exists(txt_path):
                    with open(txt_path, "r", encoding="utf-8") as f:
                        txt_content = f.read()
                    st.subheader("分析报告文本（可复制/下载）")
                    st.text_area("地区分析报告", txt_content, height=400)
                    st.download_button("下载txt报告", txt_content, file_name=txt_path)
            else:
                st.error("未生成地区分析报告，请检查数据格式或内容。")
    else:
        st.info("请上传企业json报告并输入地区名称。")

# ========== 行业报告分析 Tab ==========（基于 IndustryAgent）
with tabs[2]:
    st.write("请上传一个行业下多个公司的JSON格式报告文件，并指定行业名称，系统将生成行业结构分析及智能摘要。")

    uploaded_jsons = st.file_uploader("上传行业公司报告（支持多文件上传）", type=["json"], accept_multiple_files=True, key="industry_jsons")
    industry_name = st.text_input("请输入行业名称（如：证券、新能源、人工智能等）", value="证券")

    if uploaded_jsons and industry_name:
        # 保存上传文件到临时目录
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_paths = []
            for file in uploaded_jsons:
                file_path = os.path.join(tmp_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())
                file_paths.append(file_path)

            st.write(f"已上传 {len(file_paths)} 个行业报告文件")
            output_json_path = os.path.join(tmp_dir, f"{industry_name}_industry_report.json")

            with st.spinner("正在生成行业分析报告，请稍候..."):
                agent = IndustryAgent()
                report = agent.analyze_industry(
                    industry_dir=tmp_dir,
                    industry_name=industry_name,
                    output_path=output_json_path
                )

            if report:
                st.success("行业分析完成！")
                st.markdown(f"📁 报告已保存至：`{output_json_path}`")

                # 展示结构化数据
                st.subheader("行业结构摘要")
                st.markdown(f"**行业名称：** {report.get('industry_name', '未知')}")
                #st.markdown(f"**公司数量：** {len(report.get('company_reports', []))}")
                st.markdown(f"**公司数量：** {report.get('companies_count', 0)}")
                #st.markdown(f"**主要结论：** {report.get('summary', '无')}")

                # 展示LLM报告
                if "llm_report" in report:
                    st.subheader("LLM智能分析报告")
                    st.markdown(report["llm_report"])

                # 尝试读取TXT报告
                txt_path = output_json_path.replace(".json", ".txt")
                if os.path.exists(txt_path):
                    with open(txt_path, "r", encoding="utf-8") as f:
                        txt_content = f.read()
                    st.subheader("分析报告文本（可复制/下载）")
                    st.text_area("行业分析报告", txt_content, height=400)
                    st.download_button("下载txt报告", txt_content, file_name=os.path.basename(txt_path))
            else:
                st.error("未生成分析报告，请检查上传的JSON文件是否格式正确。")
    else:
        st.info("请上传行业报告并输入行业名称。")



#streamlit run web_app.py