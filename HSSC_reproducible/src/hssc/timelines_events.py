"""Event labels for the numbered peaks in Figures 3-7 (supplementary tables S3-S16).

``EVENTS_BY_GROUP`` is copied verbatim from cell 33 of the OSF notebook. The labels were
written by the authors from GPT-5 mini summaries of the comments in each +/-15-day peak
window (``15_group_timelines.py --windows``) and are keyed by the month of the peak they
describe. Do not edit by hand; a label only attaches to a peak whose month matches.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# fmt: off
EVENTS_BY_GROUP = {
    "Women": [
        {"date": "2008-08-11", "label": "Reykjavík chief of police withdraws his earlier support for closing a local strip club. Debate includes hostile remarks about feminists.", "vline": True},
        {"date": "2009-11-24", "label": "Minister of Social Affairs, Árni Páll Árnason, wants gender quotas in corporate boards. Debate vilifies feminists and blames them for social ills.", "vline": True},
        {"date": "2009-03-11", "label": "Parliamentary bill on criminalizing the purchase of sex work in Iceland. Debate on whether to penalize sex workers or purchasers.", "vline": True},
        {"date": "2024-04-23", "label": "Criticism of female presidential candidates (particularly then-Prime Minister, Katrín Jakobsdóttir), links feminism to social decay.", "vline": True},        
        {"date": "2017-12-09", "label": "#MeToo movement reaches Iceland. Debate on sexual harassment, gendered power imbalances, and the political and social fallout.", "vline": True},
        {"date": "2018-10-12", "label": "University of Reykjavík fires lecturer Kristinn Sigurjónsson over sexist Facebook posts. Leaking of women's responses sparks anti-feminist backlash.", "vline": True},
        {"date": "2023-03-15", "label": "Katrín Jakobsdóttir, Prime Minister, and Þórdís KR Gylfadóttir, Minister of Foreign Affairs, travel to Ukraine amid the ongoing war. Criticism of female politicians and feminism causing national decline.", "vline": True},
        {"date": "2010-05-19", "label": "Mary Glasspool becomes first openly lesbian bishop in the Anglican Communion. Debate on women's authority in Christian churches.", "vline": True},
        {"date": "2021-09-04", "label": "Several members of the Icelandic national football team accused of sexual assault. Debate on the legitimacy of these claims, and accusations of feminists exaggerating victimhood.", "vline": True},
        {"date": "2011-08-08", "label": "Pop singer and queer activist Páll Óskar claims 'the white Christian man [...] with a Bible in one hand a gun in the other' is the only group not to face discrimination. Debate on gendered prejudice.", "vline": True},   
    ],
    "Men": [
        {"date": "2008-07-18", "label": "Swedish authorities announce new legislation on sex work, criminalizing purchasers and not sex workers. Polarized debate on men who buy sexual services.", "vline": True},
        {"date": "2011-08-08", "label": "Páll Óskar’s remarks on the white Christian man. Debate includes sarcastic remarks on the alleged dangers of men, and warnings against using recent terrorism in Norway to justify anti-male sentiment.", "vline": True},
        {"date": "2018-10-12", "label": "University of Reykjavík fires Kristinn Sigurjónsson. Discussion centers on men being broadly presumed guilty and the consequences for their careers.", "vline": True},
        {"date": "2019-10-31", "label": "The Social Democratic Alliance implements gender quotas for electoral candidate lists. Debate on whether quotas hurt gender equality by limiting men's candidacy opportunities.", "vline": True},
        {"date": "2008-02-19", "label": "A news report about Hugh Hefner and his three girlfriends appearing together on the cover of Playboy magazine. Debate on gendered sexual double standards.", "vline": True},
        {"date": "2020-06-08", "label": "Comedian Pétur Jóhann Sigfússon recorded making a racist and sexist joke. Debate on identity politics and perceived targeting of (white) men by media and activist movements.", "vline": True},
        {"date": "2017-12-08", "label": "Women in politics share stories of sexual harassment and abuse in an online group. Debate on the credibility of these accounts with sarcastic generalizations portraying men as a threat to women.", "vline": True},
        {"date": "2009-10-08", "label": "A blog post notes that women author very few of the most popular blogs. Rebuttals against feminism and gender representation.", "vline": True},
    ],

    "LGBTQIA+": [
        {"date": "2012-02-15", "label": "Primary-school teacher Snorri Óskarsson blogs that homosexuality is a sin. Debate on hate speech, teachers’ public religious views, and whether schools should fire staff to protect pupils.", "vline": True},
        {"date": "2023-04-05", "label": "A mass shooting at a Nashville elementary school reportedly carried out by a trans man. Debate treats the shooter's identity as central, framing trans people as a violent threat.", "vline": True},
        {"date": "2010-09-12", "label": "Faroese MP and religious leader Jenis av Rana publicly refused to sit at a dinner with Jóhanna Sigurðardóttir, openly lesbian Prime Minister of Iceland. Discussion includes condemnation as well as homophobia.", "vline": True},
        {"date": "2009-02-12", "label": "Jóhanna Sigurðardóttir becomes the first openly queer prime minister in the world. Discussion includes slurs and hostile generalizations, as well as supportive posts.", "vline": True},
        {"date": "2009-12-06", "label": "Pop singer Friðrik Ómar reports that he isn't allowed to perform at the Pentecostal church because of his homosexuality. Polarized debate, e.g., questions on why he would want to perform in a 'church that hates [gay men]'.", "vline": True},
        {"date": "2008-07-11", "label": "Survey reveals that 77% of Christian priests in Iceland are willing to officiate same-sex weddings. Polarized discussion centers on whether homosexuality is sinful or morally acceptable.", "vline": True},
        {"date": "2024-04-02", "label": "Announcement of Baldur Þórhallsson's presidential candidacy with his husband Felix Bergsson prominently featured. Homophobic discussion with severely transphobic tendencies (Felix Bergsson is an advocate for trans rights).", "vline": True},
        {"date": "2012-07-14", "label": "Snorri Óskarsson fired from his teaching post over his homophobic blog posts. Polarized discussion centers around freedom of speech vs. hate speech.", "vline": True},
        {"date": "2013-08-09", "label": "Controversy over a planned visit by U.S. evangelist Franklin Graham (who opposes same-sex marriage). Discussion centers around freedom of speech vs. hate speech.", "vline": True},
        {"date": "2019-07-08", "label": "Iceland passes law on gender autonomy and intersex rights. Severely transphobic discussion follows, equating trans people with paedophiles, mentally ill people, or 'men who invade women's places'.", "vline": True},
        ],

    "Foreigners, asylum seekers, refugees (general)": [
        {"date": "2008-05-15", "label": "Akranes town council collapses over disagreement about accepting 30 refugees from Iraq. Polarized debate includes both refugee support and overt racism.", "vline": True},
        {"date": "2012-05-11", "label": "Teenagers from Algeria convicted for using forged travel documents. Debate centers on what qualifies as racism, and alleged 'importation of criminals'.", "vline": True},
        {"date": "2020-09-08", "label": "Deportation of an Egyptian refugee family from Iceland sparks protests. Polarized discussion centers on claims that Middle Eastern refugees don't assimilate to Icelandic culture.", "vline": True},
        {"date": "2014-06-20", "label": "MP Sveinbjörg Birna Sveinbjörnsdóttir calls for a vote on land allocation for a mosque in Reykjavík. Polarized debate on freedom of religion vs. supposed dangers of (Muslim) immigrants.", "vline": True},
        {"date": "2011-05-11", "label": "News report on newly arrived asylum seekers accused of shoplifting. Hostile discussion about welfare abuse and cultural incompatibility.", "vline": True},
        {"date": "2016-09-18", "label": "Anti-immigrant incidents in Germany and political fallout. Debate on Iceland's capacity to accept refugees, features racism towards Middle Eastern people.", "vline": True},
        {"date": "2016-01-21", "label": "Mass sexual assaults and robberies in Cologne on New Year's Eve, with perpetrators reported to include asylum-seekers of Arab and North African origin. Racist debate follows.", "vline": True},
        {"date": "2017-09-27", "label": "UNICEF encourages Icelandic parliament to change recently passed immigration laws to protect refugee children. Racist comments equate refugee children to the luggage of 'criminals who invade the country'.", "vline": True},
        {"date": "2019-03-19", "label": "Protests by refugees calling for no more deportations and fair processing of applications lead to confrontations with the police. Discussion depicts migrants as invaders, criminals, or culturally incompatible.", "vline": True},
        {"date": "2018-06-25", "label": "Political crisis in Germany over asylum policy, dispute between Angela Merkel and Horst Seehofer on refusing entry to assylum seekers. Hostile discussion on Angela Merkel's policy, with misogynistic undertones.", "vline": True},
    ],
    "Middle East (nationalities)": [
        {"date": "2014-07-19", "label": "UN Secretary-General Ban Ki-moon calls for ceasefire on Gaza. Polarized discussion centers on the nature of war vs. genocide.", "vline": True},
        {"date": "2009-01-07", "label": "Hamas attack on Israel. Polarized discussion on the war and its consequences on human rights.", "vline": True},
        {"date": "2017-12-08", "label": "Donald Trump announces recognition of Jerusalem as the capital of Israel. Discussion involves fear of renewed violence.", "vline": True},
        {"date": "2015-09-18", "label": "Reykjavík city council agrees to boycott Israeli products during the Israeli occupation of Palestinian territories. Debate pits accusations of antisemtitism against criticism of IDF human rights violations.", "vline": True},
        {"date": "2010-06-02", "label": "Israeli military raid on the Marvi Marmara aid flotilla, during which multiple people were killed or wounded. Debate on who is to blame, each side calling the other supporters of terrorism.", "vline": True},
        {"date": "2023-12-19", "label": "Protests and a petition to withdraw Iceland from Eurovision if Israel competes. Debate on the nature of war vs. genocide, includes both overt antisemitism and Islamophobia.", "vline": True},
        {"date": "2024-05-06", "label": "A concert held in protest of Iceland's participation in Eurovision. Highly polarized discussion includes Islamophobia and accusations of antisemitism amid ongoing debate over whther Israeli actions constitute genocide.", "vline": True},
        {"date": "2018-05-18", "label": "Protests at the Gaza border coincide with the relocation of the US embassy to Jerusalem, at least 60 Palestinians killed by IDF and thousands injured. Polarized debate on who is responsible, Hamas or Israel.", "vline": True},
        {"date": "2012-11-18", "label": "Escalation of violence between Israel and Hamas. Polarized debate includes Islamophobia and accusations of antisemitism along with criticism of Israeli military actions.", "vline": True},
        {"date": "2008-01-20", "label": "Reports on power cuts in Gaza causing a humanitarian emergency. Debate centers on who is to blame, Hamas or Israel.", "vline": True},
    ], 
    "Eastern Europe (nationalities)": [
        {"date": "2022-04-10", "label": "Photos reveal mass graves and bodies on the streets of Bucha, Ukraine. Debate on Russia's stated justification of fighting neo-Nazis in Ukraine.", "vline": True},
        {"date": "2014-08-29", "label": "Reports of Russian-supplied military equipment and trained personnel reaching separatists in Ukraine. Debate includes claims of Ukraine being run by neo-Nazis and support for Russian intervention.", "vline": True},
        {"date": "2008-02-28", "label": "Kosovo declares independence. Debate on whether Iceland should recognize it, xenophobic generalizations about Albanians and Muslims.", "vline": True},
        {"date": "2015-08-30", "label": "Intensified fighting along the eastern Ukraine ceasefire line. Polarized debate on NATO's response, and Iceland's responsibility to take in refugees.", "vline": True},
        {"date": "2022-10-10", "label": "Sabotage of the Nord Stream gas pipelines. Debate on who is to blame, generalizations about Russians and the Western countries.", "vline": True},
        {"date": "2018-03-13", "label": "The nerve agent attack on Sergei and Yulia Skripal in Salisbury leading to British accusations against Russia and diplomatic expulsions. Debate over motives and consequences.", "vline": True},
        {"date": "2023-06-24", "label": "The Nova Kakhovka dam collapse and subsequent decision to close the Icelandic embassy in Moscow. Hostile generalizations on Russians and NATO countries.", "vline": True},
        {"date": "2017-07-25", "label": "Report about pro-Russian separatists in Donetsk and Luhansk, and claims that they are selling factories to Russia. Accusations of neo-Nazi influences in Ukraine.", "vline": True},
        {"date": "2024-03-09", "label": "Discussion on the Russia-Ukraine war triggered by the two-year anniversary of the Russian invasion. Debate is mostly descriptive of events rather than group-specific.", "vline": True},
        {"date": "2015-02-09", "label": "Russian ongoing takeover of the Crimean Peninsula. Discussion shows concern over escalation of the conflict.", "vline": True},
    ], 
    "Icelanders": [
        {"date": "2011-05-07", "label": "Recurring arguments on whether Iceland should join the EU. Debate centers on sovereignty and national identity.", "vline": True},
        {"date": "2008-10-26", "label": "The collapse of Iceland's banks and UK's invocation of anti-terrorism legislation against Icelandic assets. Debate calls for accountability.", "vline": True},
        {"date": "2010-06-24", "label": "Currency-swap agreement signed between the Central Bank of Iceland and the People’s Bank of China. Debate includes claims about Chinese involvement in Iceland, framed as a threat to sovereignty.", "vline": True},
        {"date": "2009-07-25", "label": "Iceland formally applies for EU membership (application was eventually withdrawn). Hostile, nationalistic discourse, claims that joining the EU would destroy Iceland's sovereignty.", "vline": True},
        {"date": "2012-02-03", "label": "Croatia EU-accession referendum. Heightened debate on Iceland's EU membership application.", "vline": True},
        {"date": "2013-11-03", "label": "No event detected. Debate over Icelandic national identity and whether Icelanders display nationalist, exclusionary or a sense of cultural superiority towards immigrants.", "vline": True},
        {"date": "2012-07-07", "label": "EU Fisheries Commissioner María Damanaki visits Iceland for accession talks. Debate on EU influence over Icelandic fishing rights and sovereignty.", "vline": True},
        {"date": "2008-03-04", "label": "MP Ögmundur Jónasson calls for Iceland to immediately sever diplomatic relations with Israel. Debate includes claims that Icelanders are antisemitic.", "vline": True},
        {"date": "2020-02-24", "label": "The first COVID-19 case in Iceland confirmed. Debate centers on related travel advisories and concerns about the lack of quarantine measures for travellers.", "vline": True},
        {"date": "2017-09-08", "label": "News report on the Icelandic government doubling its funding for refugee reception for the following year. Debate featuring xenophobic rhetoric.", "vline": True},
    ],
    "Nationalities (other)": [
        {"date": "2011-05-20", "label": "Discussion of the eurozone sovereign debt crisis and institutional responses.", "vline": True},
        {"date": "2020-02-14", "label": "Financial Times story on the Karakax list, reporting on detention criteria and the scale of Uyghur detention in Xinjiang. Discussion criticizes China and other communist regimes.", "vline": True},
        {"date": "2014-08-30", "label": "Faroese ship Næraberg had engine trouble and was initially denied assistance in Iceland. Polarized debate over whether Iceland's initial refusal of assistance was justified.", "vline": True},
        {"date": "2018-08-22", "label": "Discussion of ongoing conflict between Turkey and the US, framed as economic war sparked by US trade measures by debaters, alongside accusations of Turkey practicing 'hostage politics'.", "vline": True},
        {"date": "2015-09-11", "label": "Angela Merkel's open-door policy on refugee admissions to Germany. Debate includes hostile generalizations about Muslims and refugees.", "vline": True},
        {"date": "2017-06-22", "label": "Ongoing refugee crisis and subsequent integration challenges in Nordic countries. Islamophobic refrain of refugees as a security risk and calls for stricter immigration policies.", "vline": True},
        {"date": "2012-02-05", "label": "The Greek parliament approves controversial austerity measures tied to a €130 billion EU bailout. Discussion criticizes the EU.", "vline": True},
        {"date": "2008-06-27", "label": "A Jordanian group advocates for boycotting Danish products due to the Danish cartoons of the Prophet Muhammad. Islamophobic discussion criticizes the boycott.", "vline": True},
        {"date": "2013-11-03", "label": "No event detected. Discussion on immigration, cultural integration, and perceived threats from 'Islamization'. Multiple generalizations about Germans, Swedes, and Norwegians.", "vline": True},
        {"date": "2015-02-15", "label": "Copenhagen terrorist attacks kill two and wound five at a cultural centre and synagogue. Debate on whether the attacker was a Muslim or a Dane (framing the identities as mutually exclusive).", "vline": True},
    ],

    "Ethnicities": [
        {"date": "2020-06-07", "label": "Ongoing protests following the murder of George Floyd. Polarized discussion on the Black Lives Matter movement, debating systematic racism vs. identity politics.", "vline": True},
        {"date": "2013-10-24", "label": "News reports on a white child found living with a Roma family in Greece, allegations of child abduction. Debate criticizes racist media and public reactions towards Roma people.", "vline": True},
        {"date": "2014-08-02", "label": "Escalation of hostilities between Israel and Hamas in Gaza. Debate includes anti-Arab hostility and accusations of antisemitism.", "vline": True},
        {"date": "2008-05-25", "label": "A proposal to resettle a group of Iraqi refugees in Akranes, and public opposition by MP Magnús Þór Hafsteinsson. Debate includes hostile generalizations about Arabs.", "vline": True},
        {"date": "2009-01-07", "label": "Israeli military assault on Gaza. Debate includes hostile generalizations about 'the Arab countries' alleged plan to destroy Israel.", "vline": True},
        {"date": "2016-12-28", "label": "Multiple reports of violent crimes allegedly committed by migrants in Germany. Debate includes hostile generalizations about migrants and Arabs.", "vline": True},
        {"date": "2018-07-22", "label": "Arguments about Nelson Mandela's legacy and South Africa's treatment of white people, alongside controversy over a local band performing in blackface. Discussion centers on the nature of racism.", "vline": True},
        {"date": "2015-09-11", "label": "A spike in refugee arrivals in Iceland. Many posts express hostile generalizations about Arabs and argue against accepting refugees.", "vline": True},
        {"date": "2011-08-08", "label": "The Norway terrorist attacks by Anders Behring Breivik. Discussion includes hostile generalizations about Arabs and white Christians.", "vline": True},
        {"date": "2012-07-28", "label": "Greek athlete Voula Papachristou barred from participating in the London Olympics due to racist comments on Twitter. Debate centers on free speech.", "vline": True},
    ],

    "Islam": [
        {"date": "2014-06-07", "label": "MP Sveinbjörg Birna Sveinbjörnsdóttir makes it a campaign issue that the city's land allocation for a mosque will be revoked. Xenophobic debate follows.", "vline": True},
        {"date": "2015-01-13", "label": "Charlie Hebdo shooting. Discussion centers on the alleged dangers of Islam, immigration, and opposition to mosque construction in Reykjavík.", "vline": True},
        {"date": "2015-09-27", "label": "Surge of refugees into Europe (and reactions to Angela Merkel's open‑door stance) and Reykjavík city‑council proposal of boycotting Israeli products. Islamophobic debate, accusations of antisemitism.", "vline": True},
        {"date": "2017-06-11", "label": "Reports of Islamist attacks in the UK (London Bridge attack, Manchester attack, and others). Debate frames Muslims as a security threat and culturally incompatible with Western society.", "vline": True},
        {"date": "2016-07-31", "label": "Reports of Islamist attacks in Nice, France, where a truck was driven into crowds celebrating Bastille Day. Hostile generalizations about Muslims, immigrants, and lack of cultural assimilation.", "vline": True},
        {"date": "2008-06-08", "label": "Akranes town council passes a motion to receive refugees to the town, leading to internal debates and the council's collapse. Hostile generalizations about Muslims.", "vline": True},
        {"date": "2013-07-21", "label": "A plot allocated to The Icelandic Muslim Association for mosque construction in Reykjavík. Heated debate and xenophobic criticism.", "vline": True},
        {"date": "2018-06-25", "label": "No event detected. A wave of hostile discourse about Muslims, portraying Islam as inherently violent and incompatible with Western society. Objections to headscarves and mosques.", "vline": True},
        {"date": "2012-09-21", "label": "Publication of Muhammad cartoons and release of the film Innocence of Muslims spark protests across Muslim countries, Western embassy closures, and violence, including the death of US ambassador in Libya. Anti-Muslim rhetoric.", "vline": True},
        {"date": "2020-09-23", "label": "Reports on an Egyptian family being deported from Iceland. Hostile generalizations about Muslim immigrants and asylum-seekers.", "vline": True},
    ],
    "Judaism": [
        {"date": "2014-07-19", "label": "Israeli airstrikes on Gaza and reciprocal rocket attacks by Hamas. Debate includes comparisons to the Holocaust, as well as Islamophobic rhetoric and accusations of antisemitism.", "vline": True},
        {"date": "2011-12-27", "label": "Sparked by Haaretz article about Jews in Iceland and the follow-up Icelandic media coverage, debate centers on antisemitism in Iceland and whether criticism of Israel constitutes anti‑Jewish hostility.", "vline": True},
        {"date": "2015-10-23", "label": "Debate on whether Israel is committing a genocide against Palestinians and whether framing Israeli actions as genocide constitutes antisemitism.", "vline": True},
        {"date": "2012-11-27", "label": "Outbreak of hostilities between Israel and Hamas. Polarized debate on alleged media bias and pro‑ or anti‑Jewish sentiment in Icelandic politics and society.", "vline": True},
        {"date": "2010-06-02", "label": "Israeli forces attack Gaza-bound aid flotilla, resulting in multiple deaths and widespread international outcry. Accusations of antisemitism in Icelandic politics and society.", "vline": True},
        {"date": "2023-12-16", "label": "Protest at a University of Iceland event, calling for political action and a trade boycott of Israel. Debate includes condemnation of the Israeli genocide and accusations of antisemitism.", "vline": True},
        {"date": "2017-12-16", "label": "Donald Trump recognizes Jerusalem as Israel's capital and announces plans to move US embassy there. Polarized debate includes clearly antisemitic and Islamophobic remarks.", "vline": True},
        {"date": "2008-12-28", "label": "A major Israeli military operation in Gaza with large numbers of Palestinian civilian casualties and international condemnation. Debate includes accusations of war crimes and media bias.", "vline": True},
        {"date": "2018-05-20", "label": "Mass protests at the Gaza–Israel border in which dozens of Palestinians were killed. Polarized discussion on who is to blame, IDF or Hamas.", "vline": True},
        {"date": "2008-03-04", "label": "MP Ögmundur Jónasson calls for immediate sever of diplomatic relations with Israel. Polarized debate includes both Islamophobia and antisemitism.", "vline": True},
    ], 
    "Christianity": [
        {"date": "2008-09-16", "label": "No event detected. Heated debate between Christian and atheist bloggers on creationism vs. Darwinian evolution, each accusing the other of ignorance.", "vline": True},
        {"date": "2014-06-24", "label": "Sveinbjörg Birna Sveinbjörnsdóttir's comments on land allocation for a mosque. Islamophobia and comparison between Christian scripture and Islamic practices.", "vline": True},
        {"date": "2012-02-24", "label": "Primary-school teacher Snorri Óskarsson's dismissal following his homophobic blogs. Debate on freedom of religion vs. freedom of speech.", "vline": True},
        {"date": "2017-06-25", "label": "No event detected. Hostile debate frames Muslims as inherently violent terrorists. Responses frame Christianity as equally violent.", "vline": True},
        {"date": "2009-05-19", "label": "Media coverage of the fossil Ida, nicknamed the 'missing link', and related claims about human evolution. Broad hostile generalizations about Christians.", "vline": True},
        {"date": "2015-10-19", "label": "No event detected. Criticism and hostile generalizations about the perceived hypocrisy of Christian institutions and believers, historical violence and misogyny in the church.", "vline": True},
        {"date": "2010-09-16", "label": "Faroese MP and Christian preacher Jenis av Rana refuses to sit with Icelandic PM Jóhanna Sigurðardóttir due to her homosexuality. Debate includes claims that this is not what Christianity is about.", "vline": True},
        {"date": "2015-01-04", "label": "Charlie Hebdo attack. Hostile generalizations about Muslims, claims that left-wing political parties in Iceland favor minorities and thereby undermine the national church.", "vline": True},
        {"date": "2011-07-24", "label": "The terrorist attacks in Norway by Anders Behring Breivik. Debate centers on whether Breivik should be considered Christian and whether such violence is linked to his Christianity.", "vline": True},
        {"date": "2008-01-01", "label": "Recent media coverage about Icelandic primary-school law removing references to 'Christian ethics'. Criticism of Christianity in historical and contemporary context.", "vline": True},
    ],      
    "Religion (other)" : [
        {"date": "2010-07-18", "label": "Heated debate between atheists and Christians on the platform, citing a recently published article by Dr. John R. Mabry in Philosophy Now. Centers on whether atheism is in itself a religion.", "vline": True},
        {"date": "2011-08-31", "label": "Debate on whether religion or atheism is more responsible for violence and moral failure. Participants cite recent news of violence (including Breivik) to argue for or against religion as the root cause of violence.", "vline": True},
        {"date": "2009-05-19", "label": "Dalai Lama visits Iceland. Debate contrasts defense of Christian faith and the claim that morality comes from God, with assertions that morality is independent of belief.", "vline": True},
        {"date": "2015-09-28", "label": "No event detected. A cluster of comments featuring generalizations about Muslims as well as religious people in general.", "vline": True},
        {"date": "2010-02-19", "label": "No event detected. Debate over religion vs. atheism, specifically whether the atheist group Vantrú constitutes a religious organization and whether morality can be grounded without god.", "vline": True},
        {"date": "2008-05-30", "label": "No event detected. A poll posted on a blog about which group is more hostile, Christians or members of Vantrú.", "vline": True},
        {"date": "2014-12-24", "label": "Primary school trips to religious institutions banned in Iceland. Cluster of comments debating perceived attacks on Christian culture and accusations that politicians seek to marginalize the national church.", "vline": True},
        {"date": "2013-09-04", "label": "No event detected. Debate over whether atheism is hostile to religion and whether widespread atheism leads to social harm.", "vline": True},
    ],
    "Religious people (general terms)": [
        {"date": "2010-08-05", "label": "No event detected. Cluster of comments about atheism vs. religion, how critical thinking relates to faith, and complaints about censorship on the platform.", "vline": True},
        {"date": "2008-09-16", "label": "No event detected. Debate over religion vs. science with generalizations about religious groups. Claims that belief is irrational and even dangerous.", "vline": True},
        {"date": "2009-05-18", "label": "Four MPs do not attend the mass traditionally held at the reopening of the Icelandic parliament after summer recess. Debate about church-state rituals.", "vline": True},
        {"date": "2012-02-15", "label": "Primary school teacher Snorri Óskarsson's blogs on homosexuality as a sin. Debate on whether the blogs constitute hate speech or freedom of religion.", "vline": True},
        {"date": "2012-07-31", "label": "The public dismissal of Snorri Óskarsson. Debate over public expressions of religious belief and their limits.", "vline": True},
        {"date": "2010-02-19", "label": "No event detected. Heated argument between religious commenters and atheists.", "vline": True},
        {"date": "2011-08-31", "label": "No event detected. Debate linking religion to violence and social harm, includes references to Breivik.", "vline": True},
        {"date": "2014-06-21", "label": "MP Sveinbjörg Birna Sveinbjörnsdóttir's comments on land allocation for a mosque. Debate mixes Islamophobia and broad generalizations on religious people.", "vline": True},
        {"date": "2008-01-01", "label": "A heated debate about priests' visits to preschools and primary schools and whether they constitute proselytizing.", "vline": True},
        {"date": "2018-01-04", "label": "Publication of the 2018 government budget proposal, showing 6.5 billion ISK allocated to religious institutions. Debate on the privileged status of the national church.", "vline": True}
    ], 
    
    "Disability": [
        {"date": "2009-09-09", "label": "A blog post mocks drunken men by portraying their postures as yoga poses. Hostile generalizations on substance use and mental illness, debate on whether alcoholism is a disease or a choice.", "vline": True},
        {"date": "2009-03-26", "label": "News on a large local cannabis bust sparked debate over legalization versus strict punishment, alongside hostile generalizations about drug users and an explicitly ableist remark.", "vline": True},
        {"date": "2008-07-04", "label": "Protests against a rehab facility being placed in a Reykjavík neighborhood. Debate over child safety vs. the need for treatment, broader discussion of addiction stigma and causes.", "vline": True},
        {"date": "2008-01-12", "label": "A photo of a televangelist parking in a disabled space sparked debate on disrespect toward disabled people and alleged exploitation by religious fundraisers. Discussions of 'welfare cheats' and media portrayals of addiction.", "vline": True}
    ],

}
# fmt: on


def events_with_peak_ranks(group_name: str, shown_peaks: pd.DataFrame) -> list[dict]:
    """One row per shown peak (by ``display_rank``) with the event whose date falls in the
    peak month (``_events_with_peak_ranks`` in the notebook, with EVENT_MATCH_EXACT_ONLY=True)."""
    if shown_peaks is None or shown_peaks.empty:
        return []

    events = []
    for e in EVENTS_BY_GROUP.get(group_name, []):
        d = pd.to_datetime(e.get("date"), errors="coerce")
        if pd.isna(d):
            continue
        events.append({"date": d, "label": str(e.get("label", "")).strip()})

    p = shown_peaks[["month", "display_rank"]].copy()
    p = p.dropna().drop_duplicates(subset=["display_rank"]).sort_values("display_rank")

    rows, used = [], set()
    for _, pr in p.iterrows():
        peak_month = pd.to_datetime(pr["month"])
        hit = next((i for i, ev in enumerate(events)
                    if i not in used and ev["date"].to_period("M") == peak_month.to_period("M")), None)
        if hit is None:
            rows.append({"peak_rank": int(pr["display_rank"]), "peak_month": peak_month,
                         "label": "No mapped event for this peak month", "delta_days": np.nan})
        else:
            used.add(hit)
            rows.append({"peak_rank": int(pr["display_rank"]), "peak_month": peak_month,
                         "label": events[hit]["label"], "delta_days": 0.0})
    return rows
