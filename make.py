import json, os, subprocess, sys, shutil
from playwright.sync_api import sync_playwright

V = [
 dict(id=1, name="元彼", time="0:12",
  chat=[["them","元気？"],["them","最近ふと思い出して連絡しちゃった"],["me","え、ひさしぶり！元気だよ"],["them","よかった。今度ちょっと話せない？"]],
  caps=dict(chat="別れて半年の元彼から<br>夜中にこれ来た…", upload="脈あり診断してみた", load="お願い…", result="え、まだワンチャンある…？"),
  score=72, label="まだ気持ちあり",
  signals=[["最近ふと思い出して","夜中に思い出す＝気持ちが残っているサイン",False],["今度ちょっと話せない？","会って話したい＝復縁を考えている可能性",False]]),
 dict(id=2, name="サークルの先輩", time="21:48",
  chat=[["me","先輩おすすめの映画ありますか？"],["them","返信遅れてごめん！最近バタバタしてて。おすすめはラストが本当に良いやつがあって、観たら感想聞かせてほしい！あと前に言ってたカフェも行けた？"]],
  caps=dict(chat="好きな先輩、返信は遅いのに<br>毎回めっちゃ長い…", upload="これって脈あり？", load="ドキドキ…", result="覚えててくれたの<br>嬉しすぎる"),
  score=68, label="脈ありより",
  signals=[["観たら感想聞かせてほしい","会話を続けたい気持ちの表れ",False],["前に言ってたカフェも行けた？","あなたの話をちゃんと覚えている",False]]),
 dict(id=3, name="アプリの人", time="22:05",
  chat=[["me","休日は何してるんですか？"],["them","カフェ巡りが多いです！○○さんは？甘いもの好きですか？"],["me","大好きです！"],["them","じゃあ表参道のパンケーキ気になってるんですけど、一緒にどうですか？"]],
  caps=dict(chat="マッチングアプリの人<br>これって脈あり？", upload="AIに聞いてみた", load="結果は…", result="88%は行くしかない"),
  score=88, label="かなり脈あり",
  signals=[["○○さんは？","質問返し＝あなたに興味がある",False],["一緒にどうですか？","お店まで決めて誘う＝本気度高め",False]]),
 dict(id=4, name="好きな人", time="23:30",
  chat=[["me","今度ごはん行かない？"],["them","いいね、今度ね〜"],["me","来週とかどう？"],["them","来週ちょっと忙しいかも、また連絡する！"]],
  caps=dict(chat="好きな人がずっと<br>「今度ね」しか言わない…", upload="診断してみたら", load="こわい…", result="現実見た…"),
  score=24, label="今は友達モード",
  signals=[["今度ね〜","日程を決めない＝まだ優先度は低め",True],["また連絡する！","相手から連絡が来るか様子を見よう",True]]),
 dict(id=5, name="男友達", time="20:17",
  chat=[["them","そういえばさ、今彼氏いるの？"],["me","いないよ〜なんで？"],["them","いや、別に笑 ちょっと気になっただけ"],["them","今週末ひま？"]],
  caps=dict(chat="ただの男友達だと思ってたのに<br>急にこれ聞かれた", upload="脈あり診断にかけてみた", load="まさかね…", result="え、待って…"),
  score=91, label="ほぼ確定で脈あり",
  signals=[["今彼氏いるの？","恋愛対象として見ているサイン",False],["今週末ひま？","確かめた直後に誘う＝本気",False]]),
 dict(id=6, name="気になる人", time="7:42",
  chat=[["me","今日ありがとう！楽しかった"],["them","ごめん寝てた！こちらこそめっちゃ楽しかった"],["them","次は前に言ってた水族館行かない？"]],
  caps=dict(chat="既読スルーされたと思ったら<br>翌朝これ来た…", upload="脈あり診断してみた", load="どっち…？", result="寝てただけかい"),
  score=79, label="脈ありより",
  signals=[["次は前に言ってた水族館行かない？","次の約束を自分から出す＝また会いたい",False],["めっちゃ楽しかった","「めっちゃ」は本音が出やすい言葉",False]]),
 dict(id=7, name="バイトの先輩", time="22:51",
  chat=[["them","来週のシフトいつ入ってる？"],["me","火曜と金曜です！"],["them","じゃあ金曜終わったらご飯行こ"],["them","おすすめのラーメン屋あるから"]],
  caps=dict(chat="バイトの先輩に<br>シフト聞かれたんだけど…", upload="これ脈ある？", load="お願い…", result="シフト聞いたの<br>そういうこと！？"),
  score=84, label="かなり脈あり",
  signals=[["来週のシフトいつ入ってる？","会える日を探している",False],["金曜終わったらご飯行こ","シフト確認の直後に誘う＝最初から誘うつもり",False]]),
 dict(id=8, name="元彼", time="0:00",
  chat=[["them","誕生日おめでとう"],["me","ありがとう！覚えててくれたんだ"],["them","まあね笑 元気にしてる？"]],
  caps=dict(chat="元彼から日付変わった瞬間に<br>誕生日LINE…", upload="気持ち診断してみた", load="ドキドキ…", result="ちょうど半分って<br>いちばん困る"),
  score=48, label="迷い中",
  signals=[["誕生日おめでとう","0時ちょうど＝ずっと覚えていた",False],["まあね笑","照れ隠し。でも次の誘いはまだない",True]]),
 dict(id=9, name="男友達", time="7:05",
  chat=[["them","おはよ！今日寒いからあったかくしてね"],["me","おはよ〜ありがとう"],["them","そういえば昨日言ってた映画、今週末一緒に観に行かない？"]],
  caps=dict(chat="男友達から毎朝<br>おはようLINEが来る…", upload="これ普通？AIに聞いた", load="まさかね", result="毎朝は普通じゃなかった"),
  score=82, label="かなり脈あり",
  signals=[["今日寒いからあったかくしてね","体調を気づかう＝特別に思っているサイン",False],["今週末一緒に観に行かない？","あなたの話を覚えていて誘う",False]]),
 dict(id=10, name="好きな人", time="21:12",
  chat=[["me","今日のライブめっちゃよかったね！また一緒に行きたい"],["them","👍"],["me","次いつ空いてる？"],["them","また見とく！"]],
  caps=dict(chat="好きな人の返信が<br>いつも短すぎる…", upload="診断してみたら", load="こわい…", result="短いのは<br>そういうことか…"),
  score=19, label="今は脈なし",
  signals=[["👍","スタンプ・絵文字だけ＝会話を続ける気持ちが弱め",True],["また見とく！","日程を決めない＝今は優先度が低め",True]]),
dict(id=11, name="同じクラスの人", time="22:40",
  chat=[["them","明日の課題もうやった？"],["me","まだ〜むずくない？"],["them","じゃあ明日早めに来て一緒にやろ"],["them","カフェオレおごる"]],
  caps=dict(chat="同じクラスの人に<br>課題のこと聞かれただけなのに…", upload="これ脈ある？", load="まさか…", result="課題は口実だった…？"),
  score=81, label="かなり脈あり",
  signals=[["明日早めに来て一緒にやろ","2人の時間を自分から作っている",False],["カフェオレおごる","小さなプレゼント＝好印象を持たれたい",False]]),
 dict(id=12, name="職場の先輩", time="19:58",
  chat=[["me","今日はフォローありがとうございました！"],["them","全然！おつかれさま"],["them","気をつけて帰ってね"]],
  caps=dict(chat="職場の先輩、優しいけど<br>これって脈あり…？", upload="AIに聞いてみた", load="どっち…", result="優しいだけだった…"),
  score=34, label="まだ様子見",
  signals=[["気をつけて帰ってね","気づかいはあるが、話を広げてはいない",True],["全然！おつかれさま","丁寧な社交辞令の可能性",True]]),
 dict(id=13, name="アプリの人", time="23:55",
  chat=[["them","まだ起きてる？"],["me","起きてるよ〜"],["them","なんか声聞きたくなった笑 電話できる？"]],
  caps=dict(chat="マッチングアプリの人から<br>深夜にこれ来た…", upload="脈あり診断してみた", load="ドキドキ…", result="深夜の電話は…<br>ちょっと慎重に"),
  score=61, label="好意はありそう",
  signals=[["声聞きたくなった","会話したい気持ちはある",False],["まだ起きてる？","深夜だけの連絡なら様子を見よう",True]]),
 dict(id=14, name="元彼", time="21:03",
  chat=[["them","この前インスタのストーリー見た"],["them","髪切ったんだね、似合ってた"],["me","え、ありがとう笑"]],
  caps=dict(chat="元彼が私のストーリーに<br>反応してきた…", upload="気持ち診断してみた", load="お願い…", result="まだ見てくれてたんだ…"),
  score=67, label="まだ気になっている",
  signals=[["ストーリー見た","わざわざ伝える＝まだ気にしている",False],["似合ってた","見た目をほめる＝好意の名残",False]]),
 dict(id=15, name="男友達", time="18:22",
  chat=[["me","今日の飲み会来る？"],["them","みんな来るなら行こうかな"],["them","てか○○も来る？"]],
  caps=dict(chat="男友達が飲み会で<br>私の友達のこと聞いてきた…", upload="これってどういうこと？", load="こわい…", result="私じゃなかった…"),
  score=12, label="脈なし",
  signals=[["○○も来る？","関心はあなたの友達の方に向いていそう",True],["みんな来るなら","あなた個人への強い興味は見えない",True]]),
 dict(id=16, name="年上の人", time="20:30",
  chat=[["them","この前話してたパン屋、行ってみたよ"],["them","めっちゃ美味しかった。教えてくれてありがとう"],["me","よかった〜！"],["them","今度別のおすすめも教えて"]],
  caps=dict(chat="年上の人が私のおすすめ<br>ちゃんと行ってくれてた…", upload="これ脈あり？", load="期待しちゃう…", result="話ちゃんと聞いてくれてた"),
  score=74, label="脈ありより",
  signals=[["行ってみたよ","あなたの話を覚えて行動している",False],["今度別のおすすめも教えて","会話を続けたい気持ち",False]]),
 dict(id=17, name="好きな人", time="1:12",
  chat=[["me","今日楽しかった！"],["them","楽しかったね"],["me","また遊ぼ！"],["them","うん"]],
  caps=dict(chat="好きな人の返信が<br>オウム返しばっかり…", upload="診断したら", load="こわい…", result="がんばるしかない…"),
  score=27, label="今は友達モード",
  signals=[["楽しかったね","オウム返し＝会話を広げる気持ちは弱め",True],["うん","次の約束につながっていない",True]]),
 dict(id=18, name="バイトの後輩", time="21:47",
  chat=[["them","先輩って彼氏いるんですか？"],["me","いないよ笑 なんで？"],["them","いや、なんとなくです！"],["them","来週ひまな日ありますか？"]],
  caps=dict(chat="年下のバイトの後輩に<br>いきなりこれ聞かれた…", upload="AIに聞いてみた", load="まさか…", result="年下くん本気かも"),
  score=88, label="かなり脈あり",
  signals=[["彼氏いるんですか？","恋愛対象として確認している",False],["来週ひまな日ありますか？","確認した直後に誘う＝本気度高め",False]]),
 dict(id=19, name="気になる人", time="12:15",
  chat=[["them","昨日教えてもらった曲ずっと聴いてる"],["them","ほかにもおすすめある？"]],
  caps=dict(chat="気になる人が私の好きな曲<br>ずっと聴いてくれてる…", upload="脈あり診断", load="お願い…", result="うれしすぎて泣く"),
  score=77, label="脈ありより",
  signals=[["ずっと聴いてる","あなたの好きなものに興味を持っている",False],["ほかにもおすすめある？","話のきっかけを作ろうとしている",False]]),
 dict(id=20, name="元彼", time="2:34",
  chat=[["them","ねえ、起きてる？"],["them","なんか急に会いたくなった"],["me","どうしたの？"],["them","いや、なんでもない。ごめん"]],
  caps=dict(chat="元彼から深夜2時に<br>「会いたい」って来た…", upload="これ本気？", load="ドキドキ…", result="深夜のこれは…<br>流されないで"),
  score=42, label="気持ちが揺れている",
  signals=[["急に会いたくなった","寂しさからの連絡の可能性もある",True],["なんでもない。ごめん","本人もまだ気持ちが決まっていない",True]]),
 dict(id=21, name="同期", time="20:05",
  chat=[["them","今日のプレゼンすごかったね"],["them","資料の作り方教えてほしい"],["them","お礼にご飯おごるから笑"]],
  caps=dict(chat="会社の同期に<br>ほめられたあとこれ来た…", upload="AI診断してみた", load="期待しちゃう", result="お礼のご飯って…<br>デートじゃん"),
  score=71, label="脈ありより",
  signals=[["すごかったね","しっかり見てくれている",False],["ご飯おごるから","会う理由を自分から作っている",False]]),
 dict(id=22, name="アプリの人", time="21:21",
  chat=[["me","今週末どこか行きませんか？"],["them","今週はちょっと忙しくて…"],["them","また落ち着いたら連絡しますね"]],
  caps=dict(chat="マッチングアプリの人に<br>勇気出して誘ったら…", upload="結果は…", load="こわい…", result="次いこ次"),
  score=21, label="今は脈なし",
  signals=[["ちょっと忙しくて…","代わりの日程を出していない",True],["また落ち着いたら","やんわりした保留",True]]),
 dict(id=23, name="幼なじみ", time="22:18",
  chat=[["them","地元帰ってくるの？"],["me","年末帰るよ〜"],["them","じゃあ2人でごはん行こ"],["them","話したいことある"]],
  caps=dict(chat="幼なじみから<br>「話したいことある」って…", upload="脈あり診断", load="え、待って", result="これは告白の予感"),
  score=86, label="かなり脈あり",
  signals=[["2人でごはん行こ","「2人で」とはっきり言っている",False],["話したいことある","特別な話をするつもり",False]]),
 dict(id=24, name="好きな人", time="19:40",
  chat=[["me","この前の写真送るね！"],["them","ありがとう！いい写真"],["them","てかこの服似合ってる"]],
  caps=dict(chat="好きな人に写真送ったら<br>服をほめられた…", upload="AIに聞いてみた", load="どっち…", result="ちゃんと見てくれてる…"),
  score=69, label="脈ありより",
  signals=[["この服似合ってる","あなた自身をよく見ている",False],["いい写真","反応は前向き",False]]),
 dict(id=25, name="職場の人", time="23:02",
  chat=[["them","明日の会議の資料ってどこにある？"],["me","共有フォルダにあります！"],["them","ありがとう"]],
  caps=dict(chat="職場の気になる人から<br>夜にLINEが来た…と思ったら", upload="一応診断…", load="まあね…", result="業務連絡でした"),
  score=8, label="業務連絡",
  signals=[["資料ってどこにある？","仕事の確認だけ",True],["ありがとう","話を広げる様子はない",True]]),
 dict(id=26, name="男友達", time="20:44",
  chat=[["them","誕生日なにほしい？"],["me","え、いいよ笑"],["them","いや、ちゃんと渡したいから教えて"]],
  caps=dict(chat="男友達に誕生日プレゼント<br>何がほしいか聞かれた…", upload="これ脈ある？", load="期待しちゃう", result="ちゃんと渡したいって…"),
  score=83, label="かなり脈あり",
  signals=[["ちゃんと渡したいから","特別に喜ばせたい気持ち",False],["なにほしい？","あなたのことを知りたがっている",False]]),
 dict(id=27, name="元彼", time="18:09",
  chat=[["them","この前借りてた本返したいんだけど"],["them","郵送でいい？"]],
  caps=dict(chat="元彼から<br>「本返したい」って連絡…", upload="会う口実？", load="お願い…", result="郵送でした"),
  score=11, label="脈なし",
  signals=[["郵送でいい？","会わずに済ませたい気持ち",True],["本返したい","用件だけの連絡",True]]),
 dict(id=28, name="ジムの人", time="21:35",
  chat=[["them","今日もジムいたね！"],["them","いつも何曜日行ってるの？"],["me","火木が多いかな"],["them","じゃあ火曜一緒にトレーニングしよ"]],
  caps=dict(chat="ジムでよく会う人に<br>曜日を聞かれた…", upload="脈あり診断", load="ドキドキ…", result="火曜が楽しみすぎる"),
  score=80, label="かなり脈あり",
  signals=[["いつも何曜日行ってるの？","会える日を知りたい",False],["一緒にトレーニングしよ","自分から誘っている",False]]),
 dict(id=29, name="好きな人", time="0:47",
  chat=[["them","今日ちょっと疲れた"],["me","大丈夫？おつかれさま"],["them","○○と話すと元気出る"]],
  caps=dict(chat="好きな人に<br>「話すと元気出る」って言われた", upload="これって…", load="期待しちゃう", result="もう好きじゃん"),
  score=90, label="ほぼ確定で脈あり",
  signals=[["話すと元気出る","あなたが特別な存在になっている",False],["ちょっと疲れた","弱みを見せる＝心を許している",False]]),
 dict(id=30, name="アプリの人", time="22:10",
  chat=[["them","趣味なんですか？"],["me","カフェ巡りです！"],["them","いいですね"],["them","趣味なんですか？"]],
  caps=dict(chat="マッチングアプリの人<br>同じ質問2回してきた…", upload="これは…", load="あー…", result="ちゃんと読んでなかった"),
  score=15, label="今は脈なし",
  signals=[["趣味なんですか？(2回目)","メッセージをちゃんと読んでいない可能性",True],["いいですね","話を広げていない",True]]),
 dict(id=31, name="先輩", time="20:20",
  chat=[["them","この前の飲み会、ちゃんと帰れた？"],["me","帰れました！"],["them","よかった。心配してた"],["them","今度は2人でゆっくり飲もう"]],
  caps=dict(chat="飲み会のあと先輩から<br>心配LINEが来た…", upload="脈あり診断", load="え、待って", result="2人でって言った！？"),
  score=85, label="かなり脈あり",
  signals=[["心配してた","あなたのことを気にかけている",False],["今度は2人でゆっくり飲もう","「2人で」と誘っている",False]]),
]

FPS = 30
ENC = ["-c:v","libx264","-crf","20","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS)]
D = dict(chat=3.0, upload=1.8, load=1.5, hold=3.2, end=2.0)
COUNT_FRAMES = 30
base = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(base, "out"); os.makedirs(out, exist_ok=True)

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def still_clip(img, dur, dst):
    tmp = dst + ".tmp.mp4"
    run(["ffmpeg","-y","-framerate",str(FPS),"-i",img,"-vf",f"format=yuv420p,loop=-1:1,trim=duration={dur}",*ENC,tmp])
    os.replace(tmp, dst)

only = [int(a) for a in sys.argv[1:] if a.isdigit()]
preview = "preview" in sys.argv

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("file://"+os.path.join(base,"scene.html"))
    for v in V:
        if only and v["id"] not in only: continue
        wd = os.path.join(base, f"w{v['id']}"); shutil.rmtree(wd, ignore_errors=True); os.makedirs(wd)
        def shot(state, path, **extra):
            S = dict(v); S["state"]=state; S.update(extra)
            pg.evaluate("S=>render(S)", S)
            pg.wait_for_timeout(30)
            pg.screenshot(path=path, type="jpeg", quality=92)
        for st in ["chat","upload","load","end"]:
            shot(st, f"{wd}/{st}.jpg")
        shot("result", f"{wd}/result.jpg")
        if preview: continue
        cdir = f"{wd}/count"; os.makedirs(cdir)
        for i in range(COUNT_FRAMES):
            t = (i+1)/COUNT_FRAMES; e = 1-(1-t)**3
            caps = dict(v["caps"]); caps["result"] = None
            shot("result", f"{cdir}/{i:03d}.jpg", count=round(v["score"]*e), caps=caps)
        clips = []
        for st in ["chat","upload","load"]:
            c=f"{wd}/{st}.mp4"; still_clip(f"{wd}/{st}.jpg", D[st], c); clips.append(c)
        c=f"{wd}/count.mp4"; tmp=c+".tmp.mp4"
        run(["ffmpeg","-y","-framerate",str(FPS),"-i",f"{cdir}/%03d.jpg",*ENC,tmp]); os.replace(tmp,c); clips.append(c)
        c=f"{wd}/hold.mp4"; still_clip(f"{wd}/result.jpg", D["hold"], c); clips.append(c)
        c=f"{wd}/end.mp4"; still_clip(f"{wd}/end.jpg", D["end"], c); clips.append(c)
        lst=f"{wd}/list.txt"; open(lst,"w").write("".join(f"file '{x}'\n" for x in clips))
        final=os.path.join(out, f"myakumiru_{v['id']}.mp4"); tmp=final+".tmp.mp4"
        run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c","copy","-movflags","+faststart",tmp]); os.replace(tmp,final)
        print("done", final)
    b.close()
