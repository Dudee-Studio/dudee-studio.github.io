#!/usr/bin/env python3
"""Generate/cache the requested German narration and instrumental bed.
Credentials: ELEVENLABS_API_KEY or --key-file outside the repository. Never logged.
"""
import argparse
import hashlib
import concurrent.futures
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE = 'jT8mmBPqq9y1EwCWYWKS'
MUSIC_PROMPT = '''Original instrumental soundtrack for a friendly modern grocery-planning app advertisement. 112 BPM, upbeat indie-electro pop with an organic funky bass groove, warm guitar and keyboard accents, crisp but soft human-feeling drums, subtle claps and tasteful rhythmic fills. Mature, confident, approachable, fresh and positive. NOT a repetitive generic corporate loop, NOT childish, no nursery or toy xylophone sound, no dramatic epic orchestra. Leave ample midrange space for a female German voice-over. A catchy short opening motif in the first 3 seconds; light groove from 3 to 18 seconds; tasteful rhythmic lift and fresh instrumental variation between 18 and 35 seconds; another subtle melodic variation from 35 to 50 seconds; resolve with a memorable clean musical ending from 54 to 60 seconds. Controlled dynamics, polished commercial mix, no abrasive treble. Strictly instrumental: no singing, no voices, no spoken words. Do not imitate an existing song or artist.'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['speech', 'music'])
    ap.add_argument('--key-file')
    ap.add_argument('--kind', choices=['overview', 'teaser', 'store42', 'all'], default='all')
    ap.add_argument('--music-brief', help='JSON with prompt, duration_ms and repository-relative output')
    args = ap.parse_args()
    key = Path(args.key_file).read_text().strip() if args.key_file else os.environ.get('ELEVENLABS_API_KEY')
    if not key:
        raise SystemExit('ElevenLabs credential is not configured')

    def request(endpoint, payload, output):
        fingerprint = hashlib.sha256(json.dumps({k:v for k,v in payload.items() if k not in ['previous_text','next_text']},sort_keys=True).encode()).hexdigest()
        stamp = output.with_suffix('.fingerprint')
        if output.exists() and output.stat().st_size > 1000 and (not stamp.exists() or stamp.read_text().strip() == fingerprint):
            stamp.write_text(fingerprint + '\n')
            return {'path':str(output.relative_to(ROOT)), 'cached':True}
        req = urllib.request.Request('https://api.elevenlabs.io' + endpoint,
            data=json.dumps(payload).encode(), method='POST',
            headers={'xi-api-key':key, 'Content-Type':'application/json', 'Accept':'audio/mpeg'})
        try:
            with urllib.request.urlopen(req, timeout=240) as response:
                body = response.read()
                if len(body) < 1000:
                    raise RuntimeError('Audio response too short')
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(body)
                stamp.write_text(fingerprint + '\n')
                return {'path':str(output.relative_to(ROOT)), 'bytes':len(body), 'request_id':response.headers.get('request-id')}
        except urllib.error.HTTPError as e:
            try:
                detail = json.loads(e.read()).get('detail',{})
                status = detail.get('status','request_denied') if isinstance(detail,dict) else 'request_denied'
            except Exception:
                status = 'request_denied'
            raise RuntimeError(f'ElevenLabs HTTP {e.code}: {status}') from None

    if args.mode == 'music':
        brief = json.loads(Path(args.music_brief).read_text()) if args.music_brief else {}
        prompt = brief.get('prompt', MUSIC_PROMPT)
        duration = brief.get('duration_ms', 60000)
        output = ROOT / brief.get('output', 'assets/audio/abgehakt-instrumental.mp3')
        result = request('/v1/music?output_format=mp3_44100_128',
            {'prompt':prompt, 'music_length_ms':duration, 'force_instrumental':True, 'model_id':'music_v1'}, output)
        metadata = output.with_name(output.stem + '-source.json') if args.music_brief else ROOT/'assets/audio/music-source.json'
        metadata.write_text(json.dumps({'provider':'ElevenLabs','model':'music_v1','prompt':prompt,'duration_ms':duration,**result},ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(result))
        return

    jobs = []
    for kind in (['overview','teaser'] if args.kind == 'all' else [args.kind]):
        path = ROOT / f'assets/audio/de/{kind}-script.json'
        data = json.loads(path.read_text())
        data['profile'].update({'voice_id':VOICE,'voice_name':'Emily E. - First-Person Games & Audiobooks','status':'Selected from available professional voices: German, female, young.'})
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        for i, segment in enumerate(data['segments']):
            if segment.get('audio_kind', kind) != kind:
                continue  # Reuse a generated clip from the other cut.
            model = data['profile'].get('model', 'eleven_multilingual_v2')
            payload={'text':segment.get('performance_text', segment['text']),'model_id':model,'seed':7031,
                     'voice_settings':data['profile'].get('voice_settings', {'stability':0.45,'similarity_boost':0.75,'style':0.2,'use_speaker_boost':True,'speed':1.03})}
            if model != 'eleven_v3':
                if i: payload['previous_text']=data['segments'][i-1]['text']
                if i+1<len(data['segments']): payload['next_text']=data['segments'][i+1]['text']
            audio_index = segment.get('audio_index', i)
            jobs.append((kind,audio_index,payload,ROOT/f'assets/audio/de/{kind}/{audio_index:02d}.mp3'))
    results=[]
    def generate(job):
        kind,index,payload,output=job
        result=request(f'/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128',payload,output)
        print(json.dumps({'kind':kind,'index':index,**result}),flush=True)
        return {'kind':kind,'index':index,**result}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(generate,jobs): results.append(result)
    (ROOT/('assets/audio/de/store42-generation.json' if args.kind == 'store42' else 'assets/audio/de/generation.json')).write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
