import json, os, shutil

seti_path = r"C:\Users\hopcy\AppData\Local\Programs\Microsoft VS Code\6a49527b96\resources\app\extensions\theme-seti\icons"
out_dir = r"D:\dev\python\nexy\extensions\vscode\fileicons"

shutil.copy2(os.path.join(seti_path, "seti.woff"), os.path.join(out_dir, "seti.woff"))

with open(os.path.join(seti_path, "vs-seti-icon-theme.json"), encoding="utf-8") as f:
    seti = json.load(f)

seti["iconDefinitions"]["_nexy"] = {"iconPath": "./nexy.svg"}
seti["iconDefinitions"]["_nexy_light"] = {"iconPath": "./nexy-light.svg"}

seti["fileExtensions"]["nexy"] = "_nexy"
seti["fileExtensions"]["mdx"] = "_nexy"
seti["languageIds"]["nexy"] = "_nexy"
seti["languageIds"]["mdx"] = "_nexy"

light = seti.get("light", {})
seti["light"] = light
lex = light.get("fileExtensions", {})
light["fileExtensions"] = lex
lex["nexy"] = "_nexy_light"
lex["mdx"] = "_nexy_light"
lid = light.get("languageIds", {})
light["languageIds"] = lid
lid["nexy"] = "_nexy_light"
lid["mdx"] = "_nexy_light"

out_path = os.path.join(out_dir, "nexy-icon-theme.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(seti, f, ensure_ascii=False, indent=2)

n = len(seti["iconDefinitions"])
print("Written %s" % out_path)
print("iconDefinitions: %d" % n)
print("fileExtensions: %d" % len(seti["fileExtensions"]))
print("fileNames: %d" % len(seti["fileNames"]))
print("languageIds: %d" % len(seti["languageIds"]))
