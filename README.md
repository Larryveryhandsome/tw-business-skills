# tw-business-skills

台灣小型事業與不動產門市用的 **Claude Code 技能包**：8 個技能，涵蓋勞動法規檢核、法律紅旗、報告網頁、客戶網站、會議整理、現金流試算、不動產單據、事業證偽。

> **重要聲明**：本套件是 AI 助理用的「檢核流程與計算工具」，**不是法律、稅務、勞動或會計專業意見**。條文與數字會修正，法規基準日為 2026-10-24。涉及簽約、募資、僱用、報稅時，請洽律師、會計師或主管機關。

## ⚠️ 免責聲明（法律、勞動相關技能）

`tw-labor-compliance-check`（勞基法計薪排班檢核）與 `tw-legal-redflag-check`（法律紅旗檢查）兩個技能：

- 產出的結果**原則上僅供參考，不構成法律、勞動、稅務或會計專業意見**，也不保證找出所有風險。
- 法規、基本工資、國定假日與實務見解會變動，個案以主管機關、法院認定為準。
- 正式計薪、簽約、對外募資、處理勞資爭議前，**請洽勞動局、會計師或執業律師確認**。
- 作者與貢獻者不對依本套件結果所做的任何決定負責（另見 LICENSE 的 Disclaimer of Warranty）。

## 內容

| 技能 | 做什麼 | 附工具 |
|---|---|---|
| `tw-labor-compliance-check` | 小店計薪、排班、投保的合規檢核，輸出紅黃綠燈表 | `wage_calc.py` 薪資與加班費試算 |
| `tw-legal-redflag-check` | 合約、募資、平台、廣告的法律紅旗矩陣與給律師的問題清單 | — |
| `premium-report-webpage` | 把研究／SOP／筆記排成高質感單檔網頁，顏色字體可設定 | `render_tokens.py`、網頁範本 |
| `client-brand-site-builder` | 為小商家把 brief 與照片做成單頁網站並部署 | — |
| `chat-meeting-digest` | 會議逐字稿與聊天匯出檔整理成決議、待辦、跟進清單 | `parse_line_export.py`（匿名化＋筆數核對） |
| `property-cashflow-calc` | 貸款對帳、包租回本與降租情境、出租方案比較 | `loan_calc.py`（PMT／NPER／回本） |
| `brokerage-forms-a4` | 斡旋金簽收單、補充協議、租賃確認表、點交確認書 | `make_receipt.py`（含國字大寫金額、PDF 頁數驗證） |
| `venture-falsify-kpi` | 事業構想證偽、KPI 反推、App 構想轉開發指南 | — |

## 安裝

1. 下載或 clone 本 repo。
2. 把要用的技能資料夾複製到 Claude Code 的技能目錄：
   ```
   cp -r skills/<技能名稱> ~/.claude/skills/
   ```
   Windows 的 `~` 是 `C:\Users\<你的帳號>`。
3. 需要品牌色、抬頭、費率的技能，複製設定檔再改：
   ```
   cp config/brand.example.toml brand.toml
   ```
   `brand.toml` 內有你的公司資料，**不要上傳到公開處**（已列入 `.gitignore`）。
4. 重新開啟 Claude Code，直接用口語觸發，例如「幫我看這份班表合不合法」。

## 測試

需要 Python 3.11 以上（用到 `tomllib`）。

```
python -X utf8 -m unittest discover -s tests -v
```

## 已知限制

- 條文查證：勞基法 §24、§30-1、§36、§38，銀行法 §29、§29-1，民法 §249，經紀業條例 §32，公平交易法 §25 已對照全國法規資料庫；其餘標示「未查證」，請自行核對。
- 加班費倍率中的「休息日 4／8／12 小時計算單位」「2.67 倍」屬施行細則或解釋，使用前請核對現行函釋。
- 仲介報酬上限、押金上限等數字**刻意不內建**，請填入設定檔。
- 兩個法律類技能（`tw-labor-compliance-check`、`tw-legal-redflag-check`）建議先由專業人士審閱條文表再用於商業決策。
- LINE 匯出格式各版本略有差異，解析工具以合成範例測試，使用真實匯出檔前請先小檔試跑。
- PDF 輸出需要本機有 Chrome 或 Edge。

## 🛠️ 需要客製化？

這個套件是開源的，可以免費使用。如果你想要：

- 改成符合你們公司流程、單據、品牌的版本
- 串接你現在在用的系統（LINE、Google 表單、POS、會計軟體……）
- 幫你安裝、教學，或長期維護

歡迎加 LINE 跟我們聊。我們會依需求的範圍與複雜度報價，原則上以實際報價單為準。

<a href="https://lin.ee/pdYGARu"><img src="https://scdn.line-apps.com/n/line_add_friends/btn/zh-Hant.png" alt="加入好友" height="36"></a>

- 💬 LINE 官方帳號：[@812ibtir](https://lin.ee/pdYGARu)（請註明「tw-business-skills 客製化」）
- 🏢 留白事務所：網頁設計、AI 自動化、房仲遠端助理
- 👤 作者：[留白事務所](https://github.com/Larryveryhandsome)

## 授權

[Apache License 2.0](LICENSE)
