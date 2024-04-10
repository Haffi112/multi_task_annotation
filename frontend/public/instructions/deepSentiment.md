# Lyndisgreining (e. Sentiment Analysis)

Lyndisgreining er aðferð í málvinnslu sem merkir viðhorf í mismunandi texta, svo sem jákvætt, neikvætt, hlutlaust og stundum sértækari viðhorf. Fjölflokkagreining reynir að ná yfir fleiri hliðar viðhorfs í texta og veitir dýpri skilning umfram einfalda flokkun á jákvæðri eða neikvæðri afstöðu.

Hér verður notast við fjóra flokka/spurningarlista (S1-S4).

#### S1: Hvert er tilfinningalegt ástand höfundar?

- **Jákvætt:** vísbendingar eru í textanum sem benda til þess að höfundur sé í jákvæðu ástandi, þ.e. glaður, afslappaður, o.s.frv.

- **Neikvætt**: vísbendingar eru í textanum sem benda til þess að höfundur sé í neikvæðu ástandi, þ.e. dapur, reiður, kvíðinn, ofbeldisfullur o.s.frv. 

- **Blendnar tilfinningar**:  vísbendingar eru í textanum sem benda til þess að höfundur upplifi bæði jákvæðar og neikvæðar tilfinningar

- **Óþekkt**: engar vísbendingar eru í textanum um tilfinningalegt ástand höfunds.

#### S2: Hvert er aðalviðfangsefni höfundar?
- Hér er merkimiðinn opinn flokkur og er þá aðalviðfangsefni höfundar. Ef fleiri en eitt viðfangsefni eru í ummælum höfundar þá á að velja það efni sem höfundur gerir hæst undir höfði.

- Aðalviðfangsefni getur verið manneskja, hópur, hlutur, stofnun eða svipað einindi *(e. entity)*.

- Ef margar leiðir eru til þess að vísa í viðfangsefni þá skal nota þá aðferð sem höfundurinn notar. T.d. ef höfundur vísar til Barack Obama sem *hann* eða *forsetinn* þá skal nota þá mynd. <ath>Spurning hvort það ætti þá að hafa orð í nefnifalli?</ath>

#### S3: Hvað lýsir best viðhorfi, mati eða dómgreind viðmælanda gagnvart aðalviðfangsefni?
- **Jákvætt:** vísbendingar eru í textanum sem benda til þess að viðhorf höfundar til viðfangsefnis sé jákvætt (þakklátur, spenntur, bjartsýnn eða innblásinn af viðfangsefninu).

-  **Neikvætt:** vísbendingar eru í textanum sem benda til þess að viðhorf höfundar til viðfangsefnis sé neikvætt (er gagnrýninn, reiður, vonsvikinn, svartsýnn, tjáir kaldhæðni um, eða hæðst að viðfangsefni).

-  **Blandað viðhorf:** vísbendingar eru í textanum sem benda til þess að viðhorf höfundar til viðfangsefnis sé bæði jákvætt og neikvætt.

-  **Óþekkt:** það eru engar vísbendingar um viðhorf höfundar í garð viðfangsefnis.

#### S4: Hvert er almennt viðhorf flestra í garð aðalviðfangsefnisins?
- **Jákvætt:** viðfansefnið er að mestu talið jákvætt.

- **Neikvætt:** viðfangsefnið er að mestu talið neikvætt.

- **Blandað (jákvætt og neikvætt):** viðfangsefnið hefur bæði jákvæðar og neikvæðar hliðar.

- **Blandað (andstæðar fylkingar:)** viðfansefnið er er talið jákvætt af stórum hópi fólks OG er talið neikvætt af öðrum stórum hópi fólks.

- **Ekkert:** ekki skýr viðhorf í garð viðfansefnis.
 
Leiðbeiningar frá [Mohammad (2016)](https://aclanthology.org/W16-0429.pdf).