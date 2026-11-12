# -*- coding: utf-8 -*-
# システム構成と担当一覧の図（assets/system-architecture-ja.png / -en.png）を生成します。
#
#   python tools/make-architecture-png.py assets
#
# 原本は 社内資料/システム構成と担当一覧.md です。構成や担当が変わったら、
# まず原本を直し、このファイルの表（COMPONENTS・PEOPLE・RISKS ほか）を合わせてから
# 上のコマンドで PNG を作り直してください。Chrome のヘッドレスと Pillow を使います。
import io, os, shutil, subprocess, sys, tempfile

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
TMP = tempfile.mkdtemp(prefix="arch-png-")   # 中間ファイル（HTML・撮影前のPNG）の置き場

T = lambda ja, en: {"ja": ja, "en": en}

# ---------------------------------------------------------------- diagram ----
BOXES = [
    # x, y, w, h, kind, title, sub, owner
    (30, 76, 250, 82, "in", T("Zoho CRM", "Zoho CRM"),
     T("契約・ビザ・学校・書類（唯一の正）", "Contracts, visa, school, documents"), T("神田光", "Hikaru")),
    (730, 76, 250, 82, "store", T("Supabase", "Supabase"),
     T("会員データ・ログイン・MFA", "Member data, sign-in, MFA"), T("伊藤／奈須さん", "Ito / Nasu-san")),
    (1080, 76, 290, 82, "out", T("会員サイト", "Member site"),
     T("member.yume-kana.com（Azure）", "member.yume-kana.com (Azure)"), T("ヤン／伊藤", "Jan / Ito")),
    (30, 196, 250, 82, "in", T("Zoho Forms", "Zoho Forms"),
     T("お客様の書類提出の受け口", "Where member documents arrive"), T("神田光", "Hikaru")),
    (730, 196, 250, 82, "store", T("Google Drive", "Google Drive"),
     T("書類・資料／UKパスポート", "Documents, materials, UK passports"), T("神田光／ヤン", "Hikaru / Jan")),
    (380, 316, 250, 82, "in", T("管理サイト", "Admin site"),
     T("kanri.…yume-kana.com（Vercel）", "kanri.…yume-kana.com (Vercel)"), T("中村圭介", "Nakamura")),
    (1080, 316, 290, 82, "out", T("LINE・メール", "LINE and email"),
     T("リマインド・一斉連絡", "Reminders and announcements"), T("CRM", "CRM")),
]

ARROWS = [
    ("M280 117H724", T("self client / OAuth で一方向に同期", "one-way sync over self client / OAuth"), (502, 108, "middle")),
    ("M980 117H1074", None, None),
    ("M155 196V162", T("書類提出", "uploads"), (168, 184, "start")),
    ("M280 237H724", T("ファイルの保管", "file storage"), (500, 228, "middle")),
    ("M980 237H1240V162", T("書類・資料の表示", "shown to members"), (1115, 228, "middle")),
    ("M505 316V180H790V156", T("直接書き込み", "writes directly"), (645, 172, "middle")),
    ("M630 357H1074", T("一斉配信・リマインド", "announcements and reminders"), (852, 348, "middle")),
]

KIND = {
    "in":    ("#FDF3E7", "#E0913A", T("入力", "Input")),
    "store": ("#EEF1F4", "#7B8694", T("保管", "Storage")),
    "out":   ("#E7F5F3", "#39B3A6", T("出力", "Output")),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def diagram(L):
    p = ['<svg class="flow" viewBox="0 0 1400 430" xmlns="http://www.w3.org/2000/svg">',
         '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#7B8694"/></marker></defs>']
    for d, lab, pos in ARROWS:
        p.append(f'<path d="{d}" stroke="#7B8694" stroke-width="1.8" fill="none" marker-end="url(#ar)"/>')
        if lab:
            x, y, anc = pos
            p.append(f'<text x="{x}" y="{y}" class="al" text-anchor="{anc}">{esc(lab[L])}</text>')
    for x, y, w, h, k, ttl, sub, own in BOXES:
        bg, bd, tag = KIND[k]
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{bd}" stroke-width="1.8"/>')
        p.append(f'<rect x="{x}" y="{y}" width="5" height="{h}" rx="2.5" fill="{bd}"/>')
        p.append(f'<text x="{x+17}" y="{y+27}" class="bt">{esc(ttl[L])}</text>')
        p.append(f'<text x="{x+17}" y="{y+48}" class="bs">{esc(sub[L])}</text>')
        p.append(f'<text x="{x+17}" y="{y+68}" class="bo">{esc(own[L])}</text>')
        p.append(f'<text x="{x+w-12}" y="{y+22}" class="bk" fill="{bd}" text-anchor="end">{esc(tag[L])}</text>')
    p.append("</svg>")
    return "".join(p)


# ----------------------------------------------------------------- content ----
FACTS = [
    T("<b>Zoho CRM が唯一の正。</b>契約・ビザ・学校・渡航日・書類の状態は、すべて Zoho の値を表示しています。",
      "<b>Zoho CRM is the single source of truth.</b> Contracts, visa, school, departure dates and document states all come from Zoho."),
    T("<b>Zoho から Supabase へ一方向に同期します。</b>会員サイトは Supabase だけを読み、Zoho を直接見ません。",
      "<b>Zoho syncs to Supabase, one way.</b> The member site reads only Supabase and never Zoho directly."),
    T("<b>逆方向はお客様の書類提出のみ。</b>Zoho Forms を経由して Zoho に入ります。",
      "<b>Only document uploads run the other way,</b> arriving in Zoho through Zoho Forms."),
    T("<b>UK のパスポートだけ例外</b>で、Google Drive のフォルダへ直接アップロードしていただきます。",
      "<b>UK passports are the exception</b> and go straight into a Google Drive folder."),
    T("<b>管理サイトは Supabase へ直接書き込みます</b>（同期を経由しません）。",
      "<b>The admin site writes to Supabase directly,</b> bypassing the sync."),
]

COMPONENTS = [
    (T("Zoho CRM", "Zoho CRM"), T("Zoho", "Zoho"), T("神田光", "Hikaru"), T("みっちー／レオ・エミリー", "Micchi / Leo, Emily"), "o"),
    (T("Zoho Forms（書類提出）", "Zoho Forms (uploads)"), T("Zoho", "Zoho"), T("神田光", "Hikaru"), T("—", "—"), "o"),
    (T("self client（Zoho OAuth）", "self client (Zoho OAuth)"), T("Zoho", "Zoho"), T("奈須さん", "Nasu-san"), T("—", "—"), "t"),
    (T("Supabase（DB・Auth・MFA）", "Supabase (DB, auth, MFA)"), T("Supabase", "Supabase"), T("伊藤さん", "Ito-san"), T("奈須さん", "Nasu-san"), "o"),
    (T("パスワード（ログイン・多要素認証）", "Passwords (sign-in, MFA)"), T("Supabase", "Supabase"), T("マット", "Matt"), T("奈須さん", "Nasu-san"), "o"),
    (T("会員サイト", "Member site"), T("Azure", "Azure"), T("伊藤（実装）／ヤン（UI・仕様）", "Ito (build) / Jan (UI, spec)"), T("—", "—"), "o"),
    (T("管理サイト", "Admin site"), T("Vercel", "Vercel"), T("中村圭介", "Keisuke Nakamura"), T("—", "—"), "o"),
    (T("Google Drive（書類・資料）", "Google Drive (documents)"), T("Google", "Google"), T("神田光", "Hikaru"), T("ヤン（資料のリンク管理）", "Jan (material links)"), "o"),
    (T("デプロイ（本番公開）", "Deploy to production"), T("—", "—"), T("奈須さん", "Nasu-san"), T("マット", "Matt"), "o"),
    (T("リポジトリ（非公開）", "Repository (private)"), T("GitHub jstyle-yumekana/kaiin-saito", "GitHub jstyle-yumekana/kaiin-saito"), T("伊藤光司", "Koji Ito"), T("ヤン", "Jan"), "o"),
    (T("リポジトリ（プロトタイプ）", "Repository (prototype)"), T("GitHub Pages jhromek-ops/…", "GitHub Pages jhromek-ops/…"), T("ヤン", "Jan"), T("—", "—"), "o"),
]

SYNC_NOW = [
    (T("通常同期", "Regular sync"), T("10秒ごとに未処理分を確認", "Checks pending records every 10s"), "t"),
    (T("全会員の照合", "Full reconciliation"), T("毎日 午前1時", "Daily at 1:00"), "t"),
    (T("監視", "Monitoring"), T("5分ごと（遅延・権限）", "Every 5 min (delay, permissions)"), "t"),
]
SYNC_NEXT = [
    (T("書類提出まわり", "Document submission"), T("即時反映", "Immediate"), "now"),
    (T("将来の予約機能", "Future booking"), T("即時反映", "Immediate"), "now"),
    (T("それ以外すべて", "Everything else"), T("1日1回", "Once a day"), "day"),
]
API = [("5" + "分", "5 min", "約90%", "~90%"), ("30分", "30 min", "約16〜17%", "~16–17%"), ("1時間", "1 hour", "約8%", "~8%")]

PEOPLE = [
    (T("ヤン（Jan Hromek）", "Jan Hromek"), T("DX", "DX"),
     T("プロジェクト管理、会員サイトのUI・仕様、プロトタイプの原本、資料・リンク、デバッグの取りまとめ",
       "Project management, member-site UI and spec, the prototype source, materials and links, debug coordination"), "t"),
    (T("中村圭介", "Keisuke Nakamura"), T("役員", "Executive"),
     T("統括、意思決定、管理サイトの開発、権限設計", "Oversight, decisions, admin-site development, permissions design"), "x"),
    (T("神田光（ひかる）", "Hikaru Kanda"), T("DX", "DX"),
     T("Zoho CRM全般、テストアカウント、項目マッピング、Supabaseへの取り込み",
       "Zoho CRM, test accounts, field mapping, feeding Supabase"), "t"),
    (T("伊藤光司", "Koji Ito"), T("外部（ai-botec）", "External (ai-botec)"),
     T("バックエンド、同期処理、会員サイトの実装、Supabase", "Backend, sync, member-site implementation, Supabase"), "x12"),
    (T("Matthew Askett（マット）", "Matthew Askett"), T("DX", "DX"),
     T("パスワード・MFA、脆弱性対応", "Passwords and MFA, vulnerability work"), "t"),
    (T("奈須さん", "Nasu-san"), T("外部", "External"),
     T("サーバー環境、セキュリティの最終チェック、self client、デプロイ",
       "Server environment, final security review, self client, deploys"), "x"),
    (T("エミリー（Verlander）", "Emily Verlander"), T("Admin", "Admin"),
     T("ビザ業務、Zohoへのデータ移行、Edoca・TIAとの連携", "Visa work, migrating data into Zoho, Edoca and TIA"), "t"),
    (T("レオ", "Leo"), T("Admin", "Admin"), T("ビザ申請の実務", "Visa applications, hands-on"), "t"),
    (T("みっちー", "Micchi"), T("CRM", "CRM"), T("会員サイト側のCRM担当", "CRM owner for the member site"), "t"),
    (T("ゆうた", "Yuta"), T("CRM", "CRM"), T("テスト、チャットボット開発", "Testing, chatbot development"), "-"),
    (T("よっしー", "Yosshi"), T("コンサル", "Consulting"), T("お客様への案内フロー", "How members are guided"), "-"),
]

RISKS = [
    (T("伊藤さんが12月末で離任", "Ito-san leaves at the end of December"),
     T("バックエンド・同期処理・Supabaseが1人に集中。引き継ぎ先が未定です。",
       "Backend, sync and Supabase all sit with one person, with no successor named."),
     T("最優先：引き継ぎ計画と期間の確保", "Top priority: a handover plan and the time for it"), "hi"),
    (T("self client の中身が奈須さんしか見えない", "Only Nasu-san can see inside the self client"),
     T("他の人からはIPアドレスしか見えません。10/30・31のAPI逼迫の原因が特定できない直接の理由です。",
       "Everyone else sees only an IP address. This is why the Oct 30–31 API spike could not be explained."),
     T("ログ開示を依頼済み（返信待ち）", "Log disclosure requested, awaiting reply"), "hi"),
    (T("中村さんに意思決定が集中", "Decisions concentrate on Nakamura-san"),
     T("権限変更は中村さんのみ。管理サイトも単独開発です。",
       "Only he can change permissions, and he develops the admin site alone."),
     T("後からメンバー追加の想定あり", "Adding members later is foreseen"), "mid"),
    (T("奈須さんが外部で、サーバーとデプロイの要", "Nasu-san is external yet central to servers and deploys"),
     T("本番公開の主担当です。返信待ちが数日単位になることがあります。",
       "He is the owner of production deploys, and waiting for a reply can take days."),
     T("副担当にマットさんを置いています", "Matt-san is named as the second"), "mid"),
]

EXTERNAL = [
    (T("eeasy", "eeasy"), T("初回オリエン・個別面談の予約", "Orientation and counseling bookings"), T("CRM", "CRM")),
    (T("Google Classroom", "Google Classroom"), T("夢カナEnglishの課題", "Yumekana English coursework"), T("English担当", "English team")),
    (T("LINE（契約者様専用）", "LINE (members only)"), T("リマインド・一斉連絡", "Reminders and announcements"), T("CRM", "CRM")),
    (T("Edoca", "Edoca"), T("カナダのビザ申請代行（Phase 2で連携）", "Canada visa agency, linked in Phase 2"), T("エミリー", "Emily")),
    (T("TIA", "TIA"), T("オーストラリアのコンサルタント", "Australia consultant"), T("エミリー", "Emily")),
    (T("JTB", "JTB"), T("旅行手配", "Travel arrangements"), T("CRM", "CRM")),
    (T("翻訳会社・指定病院", "Translators, clinics"), T("書類の翻訳・健康診断", "Translation and medicals"), T("Admin", "Admin")),
    (T("留学バトン", "Ryugaku Baton"), T("社員情報・配信の仕組みの参考元", "Reference for staff records and announcements"), T("中村圭介", "Nakamura")),
]

OPEN = [
    (T("API上限100%到達時の挙動", "What happens at 100% of the API limit"), T("神田光 → Zoho", "Hikaru → Zoho"), T("11月9日", "Nov 9"), 0),
    (T("self client 通信内訳の開示", "Breakdown of self-client traffic"), T("伊藤 → 奈須さん", "Ito → Nasu-san"), T("返信待ち", "Awaiting reply"), 0),
    (T("書類は即時・他は1日1回の同期設計", "Sync design: documents now, the rest daily"), T("伊藤光司", "Koji Ito"), T("11月10日", "Nov 10"), 1),
    (T("初回オリエン参加日の管理方法", "How orientation attendance is recorded"), T("エミリー → CRM", "Emily → CRM"), T("11月9日", "Nov 9"), 0),
    (T("解約顧客のパスポート等の削除処理", "Deleting passports of cancelled members"), T("神田光 → CRM", "Hikaru → CRM"), T("未設定", "Not set"), 0),
    (T("脆弱性対応（AIで社内実装）", "Vulnerability work, built in-house"), T("マット", "Matt"), T("11月16〜17日", "Nov 16–17"), 0),
    (T("管理コンソールの仮版の共有", "Share the draft admin console"), T("中村圭介", "Nakamura"), T("11月11日頃", "around Nov 11"), 0),
    (T("伊藤さんからの引き継ぎ計画", "Handover plan from Ito-san"), T("—", "—"), T("未設定・最優先", "Not set, top priority"), 1),
    (T("ステージング環境の整備", "A staging environment"), T("—", "—"), T("初回公開後", "After launch"), 0),
]

MARK = {"o": ("◎", "#27AE60"), "t": ("△", "#E0913A"), "q": ("？", "#C0392B"),
        "x": ("✕", "#C0392B"), "x12": ("✕", "#C0392B"), "-": ("—", "#7B8694")}

STR = {
    "title": T("システム構成と担当一覧", "System Architecture & Ownership"),
    "sub": T("会員サイト member.yume-kana.com ／ 人が入れ替わっても引き継げる状態にするための資料です",
             "Member site member.yume-kana.com — so the project survives people changing"),
    "date": T("作成：2026年11月9日　|　2026年11月6日のミーティングでの合意事項にもとづく",
              "Prepared November 9, 2026 — based on what was agreed in the meeting of November 6, 2026"),
    "legend": T("◎ 確認済み　／　△ 関係者の記憶ベース・未検証　／　？ 不明・要確認",
                "◎ confirmed  /  △ from memory, unverified  /  ？ unknown, needs checking"),
    "s1": T("1. 全体の流れ", "1. How the pieces fit together"),
    "s2": T("2. 構成要素と担当", "2. Components and their owners"),
    "s3": T("3. 同期処理の仕様", "3. How the sync behaves"),
    "s4": T("4. 人ごとの担当", "4. Who does what"),
    "s5": T("5. 単一障害点と引き継ぎのリスク", "5. Single points of failure"),
    "s6": T("6. 外部サービス", "6. External services"),
    "s7": T("7. まだ決まっていないこと", "7. Still undecided"),
    "th_comp": T(["構成要素", "置き場所", "主担当", "副担当", "確認"],
                 ["Component", "Where it lives", "Owner", "Second", "State"]),
    "th_people": T(["氏名", "所属", "担当範囲", "代わり"], ["Name", "Team", "Responsibility", "Backup"]),
    "th_ext": T(["サービス", "用途", "担当"], ["Service", "Used for", "Owner"]),
    "th_open": T(["項目", "担当", "期限"], ["Item", "Owner", "Due"]),
    "now": T("現状（2026年11月5日 伊藤さん確認）", "Today (confirmed by Ito-san, Nov 5, 2026)"),
    "next": T("これから（2026年11月6日の決定）", "From here (decided Nov 6, 2026)"),
    "api": T("APIリクエストの試算（上限に対する消費）", "Estimated API consumption against the limit"),
    "syncwarn": T("「5分ごとに全会員を取得」という以前の共有は誤りです（11月5日・伊藤さん訂正）。"
                  "変更検知は全項目を読みに行く方式のため、項目単位で間隔を変えられるかは検証中です。",
                  "The earlier note about fetching every member every five minutes was wrong "
                  "(corrected by Ito-san on Nov 5). Change detection reads every field, so whether the "
                  "interval can be set per field is still being tested."),
    "uisrc": T("会員サイトのUIの出どころ", "Where the member-site UI comes from"),
    "uisrc_d": T("PR #7（11月6日マージ）以降、prototype.html が本番UIの唯一の原本です。"
                 "変更したら npm run build:ui を実行し、生成物も一緒にコミットしてください（CIの npm run check がずれを検出します）。",
                 "Since PR #7 (merged Nov 6), prototype.html is the only source for the production UI. "
                 "After changing it run npm run build:ui and commit the generated files; CI's npm run check catches any drift."),
    "foot": T("構成や担当が変わったら、変えた方がこの図も更新してください。△ や ？ の項目は、裏が取れた時点で ◎ に書き換えます。　"
              "原本：社内資料/システム構成と担当一覧.md",
              "If the architecture or an owner changes, whoever made the change updates this too. "
              "Anything marked △ or ？ becomes ◎ once confirmed. Source: 社内資料/システム構成と担当一覧.md"),
    "leave": T("12月末で離任", "leaves end of December"),
}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1400px;background:#EEF1F4;font-family:"Yu Gothic UI","Meiryo","Segoe UI",sans-serif;
  color:#2A3340;line-height:1.55;-webkit-font-smoothing:antialiased}
.page{padding:28px 30px 26px}
.hd{background:#1F2A44;border-radius:16px;padding:22px 28px;color:#fff;display:flex;
  justify-content:space-between;align-items:flex-end;gap:24px;margin-bottom:18px}
.hd h1{font-size:29px;font-weight:800;letter-spacing:.5px;line-height:1.25}
.hd .sb{font-size:14px;color:#AFBACA;margin-top:7px}
.hd .rt{text-align:right;flex-shrink:0}
.hd .dt{font-size:12.5px;color:#AFBACA}
.hd .lg{margin-top:9px;font-size:12.5px;font-weight:700;background:rgba(255,255,255,.1);
  border-radius:999px;padding:6px 14px;display:inline-block}
.grid{display:grid;gap:16px;margin-bottom:16px}
.g64{grid-template-columns:1.52fr 1fr}
.g55{grid-template-columns:1fr 1fr}
.card{background:#fff;border-radius:14px;padding:18px 20px 19px;box-shadow:0 4px 16px rgba(31,42,68,.05)}
h2{font-size:16px;font-weight:800;padding-left:11px;position:relative;margin-bottom:13px}
h2::before{content:"";position:absolute;left:0;top:3px;width:5px;height:17px;background:#39B3A6;border-radius:3px}
h3{font-size:12.5px;font-weight:800;color:#5B6676;margin:0 0 7px;letter-spacing:.3px}
.flow{width:100%;height:auto;display:block;margin-bottom:14px}
.bt{font-size:16px;font-weight:800;fill:#1F2A44}
.bs{font-size:12.5px;fill:#5B6676}
.bo{font-size:12px;fill:#7B8694;font-weight:700}
.bk{font-size:11px;font-weight:800;letter-spacing:.6px}
.al{font-size:11.5px;fill:#7B8694;font-weight:700}
.facts{display:grid;grid-template-columns:1fr 1fr;gap:7px 22px;border-top:1px solid #E7EBEF;padding-top:13px}
.facts div{font-size:12.5px;color:#5B6676;padding-left:21px;position:relative}
.facts div b{color:#2A3340}
.facts .n{position:absolute;left:0;top:2px;width:15px;height:15px;border-radius:50%;background:#E7F5F3;
  color:#2F9B8F;font-size:10px;font-weight:800;display:grid;place-items:center;line-height:1}
table{width:100%;border-collapse:collapse;table-layout:fixed}
table.comp col.c1{width:27%}table.comp col.c2{width:20%}table.comp col.c3{width:20%}table.comp col.c4{width:28%}
table.ppl col.c1{width:23%}table.ppl col.c2{width:12%}table.ppl col.c3{width:60%}
table.ext col.c1{width:26%}table.ext col.c2{width:50%}
table.opn col.c1{width:52%}table.opn col.c2{width:26%}
th{font-size:11px;font-weight:800;color:#7B8694;text-align:left;padding:0 8px 6px 0;
  border-bottom:1.5px solid #E7EBEF;letter-spacing:.4px;white-space:nowrap}
td{font-size:12.5px;padding:6px 8px 6px 0;border-bottom:1px solid #F1F4F6;vertical-align:top}
tr:last-child td{border-bottom:none}
td.nm{font-weight:700;color:#1F2A44}
td.mu{color:#7B8694}
td.ck{text-align:center;font-weight:800;width:34px;padding-right:0}
.tag{display:inline-block;font-size:10.5px;font-weight:800;padding:1.5px 7px;border-radius:999px;
  background:#EEF1F4;color:#5B6676;white-space:nowrap}
.tag.red{background:#FBE9E7;color:#C0392B}
.srow{display:flex;justify-content:space-between;align-items:center;gap:10px;font-size:12.5px;
  padding:6px 0;border-bottom:1px solid #F1F4F6}
.srow:last-child{border-bottom:none}
.srow span:first-child{color:#2A3340}
.pill{font-size:11.5px;font-weight:800;padding:2px 10px;border-radius:999px;white-space:nowrap}
.pill.now{background:#E7F5F3;color:#2F9B8F}
.pill.day{background:#EEF1F4;color:#5B6676}
.pill.t{background:#FDF3E7;color:#C07C25}
.sub-block{margin-bottom:12px}
.warn{font-size:12px;color:#8A5A1E;background:#FDF3E7;border-left:3px solid #E0913A;
  border-radius:0 7px 7px 0;padding:9px 12px;margin-top:11px}
.api{display:flex;gap:8px;margin-top:3px}
.api div{flex:1;background:#F7F9FA;border:1px solid #E7EBEF;border-radius:9px;padding:7px 9px;text-align:center}
.api b{display:block;font-size:11px;color:#7B8694;font-weight:800}
.api span{font-size:14px;font-weight:800;color:#1F2A44}
.risk{display:flex;gap:10px;padding:9px 0;border-bottom:1px solid #F1F4F6}
.risk:last-child{border-bottom:none}
.risk .no{width:21px;height:21px;border-radius:7px;flex-shrink:0;font-size:11px;font-weight:800;
  display:grid;place-items:center;background:#EEF1F4;color:#5B6676;margin-top:1px}
.risk.hi .no{background:#FBE9E7;color:#C0392B}
.risk .t{font-size:13px;font-weight:800;color:#1F2A44;line-height:1.4}
.risk .d{font-size:12px;color:#7B8694;margin-top:1px}
.risk .f{font-size:11.5px;font-weight:700;color:#2F9B8F;margin-top:3px}
.risk.hi .f{color:#C0392B}
.uisrc{background:#F7F9FA;border:1px solid #E7EBEF;border-radius:11px;padding:13px 15px;margin-top:13px}
.uisrc .chain{font-family:Consolas,"Courier New",monospace;font-size:12px;color:#1F2A44;
  font-weight:700;margin:6px 0 5px}
.uisrc p{font-size:12px;color:#7B8694}
.foot{text-align:center;font-size:11.5px;color:#7B8694;padding-top:4px}
"""


def page(L):
    h = [f'<!doctype html><html lang="{L}"><meta charset="utf-8"><style>{CSS}</style><body><div class="page">']
    s = {k: (v[L] if isinstance(v, dict) else v) for k, v in STR.items()}

    # header
    h.append(f'<div class="hd"><div><h1>{esc(s["title"])}</h1><div class="sb">{esc(s["sub"])}</div></div>'
             f'<div class="rt"><div class="dt">{esc(s["date"])}</div>'
             f'<div class="lg">{esc(s["legend"])}</div></div></div>')

    # 1 flow
    h.append(f'<div class="card"><h2>{esc(s["s1"])}</h2>{diagram(L)}<div class="facts">')
    for i, f in enumerate(FACTS, 1):
        h.append(f'<div><span class="n">{i}</span>{f[L]}</div>')
    h.append("</div></div>")

    # 2 components + 3 sync
    h.append('<div class="grid g64" style="margin-top:16px">')
    th = s["th_comp"]
    h.append(f'<div class="card"><h2>{esc(s["s2"])}</h2><table class="comp">'
             '<col class="c1"><col class="c2"><col class="c3"><col class="c4"><col><tr>'
             + "".join(f"<th>{esc(t)}</th>" for t in th[:-1]) + f'<th style="text-align:center">{esc(th[-1])}</th></tr>')
    for name, place, own, sec, ck in COMPONENTS:
        m, c = MARK[ck]
        h.append(f'<tr><td class="nm">{esc(name[L])}</td><td class="mu">{esc(place[L])}</td>'
                 f'<td>{esc(own[L])}</td><td class="mu">{esc(sec[L])}</td>'
                 f'<td class="ck" style="color:{c}">{m}</td></tr>')
    h.append("</table>")
    h.append(f'<div class="uisrc"><h3>{esc(s["uisrc"])}</h3>'
             '<div class="chain">prototype.html → scripts/build-original-ui.js → public/original-ui.js ほか</div>'
             f'<p>{esc(s["uisrc_d"])}</p></div></div>')

    h.append(f'<div class="card"><h2>{esc(s["s3"])}</h2>')
    h.append(f'<div class="sub-block"><h3>{esc(s["now"])}</h3>')
    for a, b, k in SYNC_NOW:
        h.append(f'<div class="srow"><span>{esc(a[L])}</span><span class="pill t">{esc(b[L])}</span></div>')
    h.append("</div>")
    h.append(f'<div class="sub-block"><h3>{esc(s["next"])}</h3>')
    for a, b, k in SYNC_NEXT:
        h.append(f'<div class="srow"><span>{esc(a[L])}</span><span class="pill {k}">{esc(b[L])}</span></div>')
    h.append("</div>")
    h.append(f'<div class="sub-block"><h3>{esc(s["api"])}</h3><div class="api">')
    for ja, en, vja, ven in API:
        h.append(f'<div><b>{esc(ja if L=="ja" else en)}</b><span>{esc(vja if L=="ja" else ven)}</span></div>')
    h.append("</div></div>")
    h.append(f'<div class="warn">{esc(s["syncwarn"])}</div></div></div>')

    # 4 people + 5 risks
    h.append('<div class="grid g64">')
    th = s["th_people"]
    h.append(f'<div class="card"><h2>{esc(s["s4"])}</h2><table class="ppl">'
             '<col class="c1"><col class="c2"><col class="c3"><col><tr>'
             + "".join(f"<th>{esc(t)}</th>" for t in th[:-1]) + f'<th style="text-align:center">{esc(th[-1])}</th></tr>')
    for name, team, duty, bk in PEOPLE:
        m, c = MARK[bk]
        extra = f' <span class="tag red">{esc(s["leave"])}</span>' if bk == "x12" else ""
        h.append(f'<tr><td class="nm">{esc(name[L])}{extra}</td><td class="mu">{esc(team[L])}</td>'
                 f'<td class="mu">{esc(duty[L])}</td><td class="ck" style="color:{c}">{m}</td></tr>')
    h.append("</table></div>")

    h.append(f'<div class="card"><h2>{esc(s["s5"])}</h2>')
    for i, (t, d, f, lv) in enumerate(RISKS, 1):
        h.append(f'<div class="risk {lv}"><div class="no">{i}</div><div>'
                 f'<div class="t">{esc(t[L])}</div><div class="d">{esc(d[L])}</div>'
                 f'<div class="f">→ {esc(f[L])}</div></div></div>')
    h.append("</div></div>")

    # 6 external + 7 open
    h.append('<div class="grid g55">')
    th = s["th_ext"]
    h.append(f'<div class="card"><h2>{esc(s["s6"])}</h2><table class="ext">'
             '<col class="c1"><col class="c2"><col><tr>'
             + "".join(f"<th>{esc(t)}</th>" for t in th) + "</tr>")
    for a, b, c in EXTERNAL:
        h.append(f'<tr><td class="nm">{esc(a[L])}</td><td class="mu">{esc(b[L])}</td><td>{esc(c[L])}</td></tr>')
    h.append("</table></div>")

    th = s["th_open"]
    h.append(f'<div class="card"><h2>{esc(s["s7"])}</h2><table class="opn">'
             '<col class="c1"><col class="c2"><col><tr>'
             + "".join(f"<th>{esc(t)}</th>" for t in th) + "</tr>")
    for item, own, due, hi in OPEN:
        cls = ' class="tag red"' if hi else ' class="tag"'
        h.append(f'<tr><td class="nm">{esc(item[L])}</td><td class="mu">{esc(own[L])}</td>'
                 f'<td><span{cls}>{esc(due[L])}</span></td></tr>')
    h.append("</table></div></div>")

    h.append(f'<div class="foot">{esc(s["foot"])}</div>')
    h.append("</div></body></html>")
    return "".join(h)


CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def render(L, out_png):
    html = os.path.join(TMP, f"arch_{L}.html")
    io.open(html, "w", encoding="utf-8").write(page(L))
    shot = os.path.join(TMP, f"shot_{L}.png")
    if os.path.exists(shot):
        os.remove(shot)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1.5", "--window-size=1400,2600",
                    f"--screenshot={shot}", "--virtual-time-budget=4000",
                    f"file:///{html.replace(os.sep, '/')}"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from PIL import Image
    im = Image.open(shot).convert("RGB")
    w, hgt = im.size
    bg = im.getpixel((5, hgt - 5))
    px = im.load()
    last = hgt - 1
    for y in range(hgt - 1, -1, -1):
        row_bg = all(px[x, y] == bg for x in range(0, w, 17))
        if not row_bg:
            last = y
            break
    im = im.crop((0, 0, w, min(hgt, last + 56)))
    # 256色に落としてファイルを小さくします。MEDIANCUT は背景などのベタ塗りを
    # そのままの色で残します（MAXCOVERAGE は色がずれるので使わないでください）。
    q = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    check = q.convert("RGB")
    probes = [(20, 300), (im.width - 20, 300), (im.width // 2, im.height - 30)]
    worst = max(max(abs(a - b) for a, b in zip(im.getpixel(xy), check.getpixel(xy))) for xy in probes)
    if worst > 2:
        sys.exit("色がずれました（最大 %d）。減色をやめて保存してください。" % worst)
    q.save(out_png, optimize=True)
    print(out_png, im.size, round(os.path.getsize(out_png) / 1024), "KB")


try:
    for lang in ("ja", "en"):
        render(lang, os.path.join(OUT, f"system-architecture-{lang}.png"))
finally:
    shutil.rmtree(TMP, ignore_errors=True)
