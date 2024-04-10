# Greining á særandi orðbragði (e. Toxicity Detection)

Greining á skaðlegu, eða særandi, orðbragði felst í að merkja texta sem slíkan og þar með greina hann frá öðrum textum sem ekki innihalda slík meiðyrði. Það er lykilþáttur í að viðhalda heilbrigðum samskiptum á netinu og nauðsynlegt fyrir sjálfvirka miðlun efnis á stafrænum vettvangi.

## Leiðbeiningar

Lögð er fram þrískipt greining:

### A: Greining á meiðyrðum

- **Ekki særandi (NOT):** Athugasemd inniheldur ekki særandi ummæli.
- **Særandi (OFF):** Athugasemdir sem innihalda óviðunandi og/eða særandi orðbragð, sem getur verið dulbúið eða beint. Þetta á við um móðganir, hótanir og athugasemdir sem innihalda niðrandi orðbragð eða blótsyrði. 

### B: Flokkun meiðyrða

- **Markviss móðgun (TIN):** Ummæli sem innihalda móðgun eða leitast eftir að særa einstakling, hóp eða aðra.
- **Ómarkvisst (UNT):** Ummæli sem innihalda ómarkviss blótsyrði, þ.e. ekki beint að neinum. 

### C: Staðfesting á marki meiðyrða

- **Einstaklingur (IND):** Athugasemir sem beinast að einstaklingi. Þetta getur verið frægur einstaklingur, nafngreindur einstaklingur eða ónefndur þátttakandi í samræðum. Móðganir og hótanir sem beinast að einstaklingum eru oft skilgreindar sem rafrænt einelti.
- **Hópur (GRP):** Athugasemdir sem beinast að hópi fólks sem talinn er vera ein heild vegna sama þjóðernis, kyns eða kynhneigðar, stjórnmálaskoðana, trúarskoðana eða annarra sameiginlegra einkenna. Margar af þeim móðgunum og hótunum sem beinast að hópi samsvara því sem almennt er skilið sem hatursorðræða. 
- **Annað (OTH):** Fórnarlamb þessara athugasemda tilheyrir engum af fyrri tveimur flokkunum (t.d. stofnanir, aðstæður, atburðir eða málefni). 

Merking gagnanna er svo stigaskipt. Ef athugasemd inniheldur ekki meiðyrði á nokkurn hátt þá er ekki merkt við flokka **B** og **C**. Eins ef athugasemd inniheldur meiðyrði en þeim er ekki beint að neinu(m), þá er **C** skilið eftir autt.

### Dæmi á ensku frá Zampieri et al.:

|Tweet|A|B|C|
|-----|-|-|-|
|@USER He is so generous with his offers.|NOT|-|-|
|IM FREEEEE!!!! WORST EXPERIENCE OF MY FUCKING LIFE|OFF|UNT|-|
|@USER Fuk this fat cock sucker|OFF|TIN|IND|
|@USER Figures! What is wrong with these idiots? Thank God for @USER|OFF|TIN|GRP|

Leiðbeiningar frá [Zampieri et al. (2019)](http://arxiv.org/abs/1902.09666).