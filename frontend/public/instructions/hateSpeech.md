# Hatursorðræðugreining (Hate Speech Detection)

Greining hatursorðræðu beinist að því að greina tungumál sem tjáir hatur eða ýtir undir ofbeldi gegn ákveðnum hópum út frá eiginleikum eins og kynþætti, trúarbrögðum, kyni eða kynhneigð.

Þrír tvíkosta flokkar eru notaðir fyrir greininguna, ásamt einum stærri flokk(?):

- **Hatursorðræða:** sýnir hvort hatursorðræða á sér stað á móti einhverjum af gefnum markhópum (konur eða innflytjendur): gildið er `1` ef svo er en annars `0`.
- **Forsendur:** Merkja skal hverjar forsendur ummælanna eru, þ.e. hvaða einkennir einstakling/hóp sem verður fyrir hatursorðræðu:
	- **Innflytjendur:** Fórnarlambið tilheyrir hópi innflytjenda eða hælisleitenda.
	- **Trúarbrögð:** Fórnarlambið tilheyrir einhverjum ákveðnum trúarhóp.
	- **Fötlun:** Fórnarlambið tilheyrir hópi fólks með fatlanir.
	- **Konur:** Fórnarlambið er eða tilheyrir hópi kvenna.
	- **Hinsegin:** Fórnarlambið tilheyrir hópi hinsegin fólks.

<ath>Ætti þetta að vera flokkað nánar? T.d. hægt að skipta hinsegin upp í kynhneigð og kynvitund. Ætti að vera sérhópur fyrir litarhaft?</ath>
- **Marksvið:** Ef hatursorðræða á sér stað er skoðað hvort fórnarlambið sé hópur fólks (merkt `0`) eða einstaklingur (merkt `1`)
- **Ágengni:** Ef hatursorðræða á sér stað er skoðað hvort höfundur sé ágengur (merkt `1`) eða ekki (merkt `0`)

Leiðbeiningar eru byggðar á [Basil et al. (2019)](https://aclanthology.org/S19-2007).

## Skilgreining hatursorðræðu

Basil et al. (2019) útvega einnig útskýringar á því hvað telst til hatursorðræðu gegn annars vegar konum og hins vegar innflytjendum. [Hér](https://github.com/msang/hateval/blob/master/annotation_guidelines.md) má finna útsýringar þeirra á ensku.

Í íslenskum lögum má finna stuttan bút sem gerir lauslega grein fyrir hatursáróðri.

**233. gr.**

>Hver, sem hefur í frammi hótun um að fremja refsiverðan verknað, og hótunin er til þess fallin að vekja hjá öðrum manni ótta um líf, heilbrigði eða velferð sína eða annarra, þá varðar það sektum …

og **233. gr. a.**

>Hver sem opinberlega hæðist að, rógber, smánar eða ógnar manni eða hópi manna með ummælum eða annars konar tjáningu, svo sem með myndum eða táknum, vegna **þjóðernisuppruna** eða **þjóðlegs uppruna**, **litarháttar**, **kynþáttar**, **trúarbragða**, **fötlunar**, **kyneinkenna**, **kynhneigðar** eða **kynvitundar**, eða breiðir slíkt út, skal sæta sektum eða fangelsi allt að 2 árum.

Þegar kemur að því hvað nákvæmlega flokkast til hatursorðræðu er ekkert til í íslenskum rétti sem skilgreinir hana. Því er hér gerð heiðarlega tilraun til þess. Líkt og bent er á í færslu á fræðslusíðunni [Hinsegin frá Ö til A](https://otila.is/vidhorf/fordomar-og-jadarsetning/hatursordraeda/) eru mismunandi skoðanir um það hvort hatursorðræða þurfi að vera skipulögð eða ekki. Dreifing bæklinga sem ráðast á minnihlutahóp sé þá skýrt dæmi um hatursorðræðu en ekki athugasemdir á samfélagsmiðlum. Samtökin '78 mótmæla þó þeirri þröngu skilgreiningu og benda á að óskipulögð ummæli á samfélagsmiðlum kynda einnig undir hatri. Hér verður notast við víðari skilgreininguna.

- **Ummæli eru hatursorðræða ef** þau leitast eftir særa, móðga eða hóta fólki eða hóp fólks (samkynhneigðir sem heild, samtök o.fl.) á grundvelli þeirra flokka sem nefndir eru [hér að ofan](#31-leiðbeiningar), hvort sem þau eru skipulögð eða ekki.

- **Ummæli eru ágeng/árásarhneigð ef** þau hóta eða ýta undir ofbeldisverk, fjandskap eða brot gegn einhverjum af [ofangreindum flokkum](#31-leiðbeiningar) eða réttlæta slíka árásarhneigð. Athugið að árásarhneigð getur verið allt frá því að vera í meðallagi (eins og félagsleg einangrun) til þess að vera mjög mikil (eins og morð).
