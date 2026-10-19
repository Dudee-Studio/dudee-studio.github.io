#!/usr/bin/env python3
"""Copy the explicitly approved landscape films and build small local previews."""
from pathlib import Path
import hashlib,json,shutil,subprocess

ROOT=Path(__file__).resolve().parents[1];ART=Path('/workspace/artifacts')
FILMS=[
 ('overview-de',ART/'abgehakt-video-v13','einkaufsliste-gerichte.mp4','abgehakt-de.vtt','overview-de.vtt','Dein Einkauf im Griff','Shopping, sorted.','de',59,3),
 ('overview-en',ART/'abgehakt-main-en-v1','abgehakt-overview-en.mp4','abgehakt-en.vtt','overview-en.vtt','Overview · English','Overview · English','en',54.833333,5.2),
 ('kostenlos',ART/'abgehakt-weitere-videos-v2/kostenlos','abgehakt-kostenlos.mp4','abgehakt-de.vtt','kostenlos-de.vtt','Kostenlose Funktionen','Free features','de',47,7),
 ('pro-version',ART/'abgehakt-weitere-videos-v2/pro-version','abgehakt-pro-version.mp4','abgehakt-de.vtt','pro-version-de.vtt','Die Pro-Version','The Pro version','de',37,7.5),
 ('analyse',ART/'abgehakt-analyse-v4','abgehakt-analyse.mp4','abgehakt-de.vtt','analyse-de.vtt','Ausgaben verstehen','Understand spending','de',27.7,5.5),
 ('community',ART/'abgehakt-weitere-videos-v2/artikelkatalog-1-1','abgehakt-community-katalog.mp4','abgehakt-de.vtt','community-de.vtt','Community-Katalog · 1.1','Community catalog · 1.1','de',33,8.5),
]
def main():
    dest=ROOT/'videos';posters=ROOT/'assets/einkaufsliste/videos';posters.mkdir(parents=True,exist_ok=True)
    entries=[]
    for fid,src,filename,cc,ccdest,de,en,lang,duration,poster_time in FILMS:
        movie=src/'abgehakt.mp4';target=dest/filename
        if movie.resolve()!=target.resolve() and (not target.exists() or hashlib.sha256(movie.read_bytes()).digest()!=hashlib.sha256(target.read_bytes()).digest()):shutil.copy2(movie,target)
        shutil.copy2(src/cc,dest/ccdest)
        poster=posters/(fid+'.jpg')
        subprocess.run(['ffmpeg','-v','error','-y','-ss',str(poster_time),'-i',str(movie),'-frames:v','1','-vf','scale=640:360',str(poster)],check=True)
        entries.append({'id':fid,'title_de':de,'title_en':en,'language':lang,'duration_sec':duration,'src':'videos/'+filename,'captions':'videos/'+ccdest,'poster':'assets/einkaufsliste/videos/'+fid+'.jpg','sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,'source':str(src),'preview':fid=='community'})
    (dest/'library.json').write_text(json.dumps({'authorization':'Nutzer: alle Querformatfilme mit kleinen Vorschauen auf die Website; Hochformate ausschließlich ins Repo.','films':entries},ensure_ascii=False,indent=2)+'\n')
    print('Prepared',len(entries),'landscape films; no portrait files added.')
if __name__=='__main__':main()
