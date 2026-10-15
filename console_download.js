(async () => {
  const urls = [
"https://images.bookdepot.com/covers/large/isbn978006/9780063205031-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978006/9780063246591-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978006/9780063448087-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978006/9780063463004-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978031/9780316585910-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978031/9780316594349-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978031/9780316597173-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978031/9780316597821-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978038/9780385548182-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978038/9780385549011-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978044/9780440000341-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593198230-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593422533-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593550328-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593642153-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593716076-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593723036-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593817322-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593817711-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593832561-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593915424-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978059/9780593955697-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978077/9780778319764-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978077/9780778387039-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978077/9780778387817-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250175236-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250210791-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250289421-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250317582-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250334237-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250335449-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250339966-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250343475-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250358196-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250362766-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250364418-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250369994-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250373625-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250375087-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250376695-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250385833-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250388483-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250396204-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250397348-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250401243-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250441171-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250468932-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250790767-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250803856-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250818584-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250822000-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250839800-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250859914-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250860057-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250871923-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250884954-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250887993-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250894724-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250902917-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978125/9781250908643-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978130/9781302911942-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978133/9781335455000-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978133/9781335574862-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978133/9781335993953-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978141/9781419772351-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978144/9781443470162-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978144/9781443473958-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978144/9781444970616-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978145/9781454950912-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978147/9781472133229-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496717276-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496735416-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496736017-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496736901-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496747747-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496753724-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496754097-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496755896-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496756145-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496757722-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496758125-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978149/9781496763709-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538718414-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538722060-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538739341-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538741818-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538769652-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538774953-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538774977-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538775448-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538778401-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538778494-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538778685-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538782040-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978153/9781538784273-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978164/9781643756288-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978164/9781645660262-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978164/9781649376510-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978164/9781649376954-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978164/9781649379412-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978164/9781649379467-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978164/9781649379740-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668001264-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668002797-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668004401-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668008034-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668009161-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668022283-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668030820-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668049532-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668049778-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668051238-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668074404-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668080009-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978166/9781668098974-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978168/9781682816301-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978168/9781682816424-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978168/9781682816516-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978168/9781682816530-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978168/9781682817292-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978172/9781728206684-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978172/9781728243177-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978172/9781728245867-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978172/9781728247205-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978172/9781728247892-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978172/9781728268910-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978172/9781728276885-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774021644-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774021712-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774021927-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774022474-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774022528-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774022535-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774022559-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774022641-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774022672-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978177/9781774022962-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978183/9781837930869-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978192/9781926444338-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978198/9781982104634-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978198/9781982170363-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978198/9781982182823-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978198/9781982197346-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978198/9781982199678-l.jpg",
"https://images.bookdepot.com/covers/large/isbn978198/9781984818546-l.jpg",
"https://images.bookdepot.com/covers/large/isbn979821/9798217187850-l.jpg"
];
  const MIN_SIZE = 5000;
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  // 选择保存文件夹；取消则退回到浏览器"下载"文件夹
  let dir = null;
  try {
    dir = await window.showDirectoryPicker({ id: "bookcovers", mode: "readwrite" });
    console.log("保存到文件夹:", dir.name);
  } catch (e) {
    console.warn("未选择文件夹，改为保存到浏览器的下载文件夹", e);
  }

  async function exists(name) {
    if (!dir) return false;
    try {
      const f = await (await dir.getFileHandle(name)).getFile();
      return f.size > MIN_SIZE;
    } catch { return false; }
  }

  async function save(name, blob) {
    if (dir) {
      const fh = await dir.getFileHandle(name, { create: true });
      const w = await fh.createWritable();
      await w.write(blob);
      await w.close();
    } else {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 15000);
    }
  }

  let ok = 0, skip = 0, consecutiveFail = 0;
  const failed = [];

  for (const [i, u] of urls.entries()) {
    const isbn = (u.match(/97[89]\d{10}/) || [""])[0];
    const name = isbn + ".jpg";
    const tag = `[${i + 1}/${urls.length}]`;

    if (await exists(name)) { skip++; continue; }

    try {
      const r = await fetch(u, { credentials: "include", cache: "no-store" });
      const ct = r.headers.get("content-type") || "";
      if (r.status === 403 || r.headers.get("cf-mitigated") === "challenge") {
        console.error(tag, "Cloudflare 403 — 刷新本页通过验证后，重新粘贴运行即可续传");
        failed.push(isbn);
        break;
      }
      if (!r.ok || !ct.startsWith("image/")) {
        console.warn(tag, "FAIL", isbn, r.status, ct);
        failed.push(isbn);
        consecutiveFail++;
      } else {
        const blob = await r.blob();
        if (blob.size <= MIN_SIZE) {
          console.warn(tag, "TOO SMALL", isbn, blob.size);
          failed.push(isbn);
          consecutiveFail++;
        } else {
          await save(name, blob);
          ok++;
          consecutiveFail = 0;
          console.log(tag, "OK", isbn, blob.size);
        }
      }
    } catch (e) {
      console.warn(tag, "ERROR", isbn, e);
      failed.push(isbn);
      consecutiveFail++;
    }

    if (consecutiveFail >= 10) {
      console.error("连续失败 10 次，停止");
      break;
    }
    await sleep(800 + Math.random() * 700);
  }

  console.log(`DONE  成功=${ok}  已存在跳过=${skip}  失败=${failed.length}`);
  if (failed.length) console.log("失败的ISBN:\n" + failed.join("\n"));
})();
