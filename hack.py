import requests
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage


gemini_2_0_flash_001 = init_chat_model("gemini-2.5-flash-preview-05-20", model_provider="google_vertexai",
                                       project='eng-genai-pilot')
gitToken=""
def get_pr_diff(repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {f"Authorization": f"Bearer {gitToken}",
               "Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)
    files = response.json()
    all_diffs = []
    for file in files:
        filename = file.get("filename")
        patch = file.get("patch")
        if patch:
            all_diffs.append(f"### File: {filename}\n{patch}\n")

    return "\n".join(all_diffs)

def analyze_diff_with_gpt(diff_text: str):
    messge = HumanMessage(content= f"""
你是一个前端智能分析助手。以下是某个 GitHub Pull Request 的前端代码变更 diff（包括 HTML、React、JSX、CSS 等）。
请根据这些改动分析是否发生了页面结构变化、按钮/组件位置变更、文案改动，列出潜在对用户操作流程的影响。

请用简洁的中文输出这些变化点：

---代码改动开始---
{diff_text}
---代码改动结束---

请输出：
1. 页面布局是否有变化（如组件顺序、位置、结构）？
2. 功能组件是否增删或移动？
3. 这些变化可能对用户产生什么影响？
""")

    response = gemini_2_0_flash_001.invoke([messge])
    return response.content

if __name__ == "__main__":
    repo = "LiveRamp/select-vm-segmentation-fe"
    pr_number = 1601  #

    print("🔍 get PR diff ing...")
    diff = get_pr_diff(repo, pr_number)
    summary = analyze_diff_with_gpt(diff)

    print("\n📄 result：")
    print(summary)