"""Build the curated review corpus used by the dashboard for TEMPER, RRR, RYALASEEMA RAMANNA CHOWDARY, and PARADISE."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reviews.csv"

META: dict[str, dict[str, object]] = {
    "TEMPER": {
        "year": 2015,
        "director": "Puri Jagannadh",
        "genre": "Action crime drama",
        "runtime": "147 min",
        "accent": "#D97706",
        "blurb": "A corrupt police inspector undergoes a ferocious moral reckoning when a horrific crime shatters his conscience.",
        "mark": "TE",
        "number": "01",
        "poster": "assets/posters/temper.jpg",
    },
    "RRR": {
        "year": 2022,
        "director": "S.S. Rajamouli",
        "genre": "Period action epic",
        "runtime": "187 min",
        "accent": "#DC2626",
        "blurb": "Two mythical revolutionaries forge an epic brotherhood before discovering their divergent missions against colonial tyranny.",
        "mark": "RR",
        "number": "02",
        "poster": "assets/posters/rrr.jpg",
    },
    "RYALASEEMA RAMANNA CHOWDARY": {
        "year": 2000,
        "director": "Suresh Krissna",
        "genre": "Faction drama",
        "runtime": "158 min",
        "accent": "#7C3AED",
        "blurb": "A revered village patriarch fights to dismantle ancestral faction feuds and protect his people's dignity with righteous authority.",
        "mark": "RC",
        "number": "03",
        "poster": "assets/posters/rayalaseema_ramanna_chowdary.jpg",
    },
    "PARADISE": {
        "year": 2023,
        "director": "Prasanna Vithanage",
        "genre": "Psychological drama",
        "runtime": "93 min",
        "accent": "#0D9488",
        "blurb": "An Indian couple's vacation in Sri Lanka unravels amid economic crisis, escalating theft, and social tensions.",
        "mark": "PA",
        "number": "04",
        "poster": "assets/posters/paradise.jpg",
    },
}

REVIEWS: dict[str, list[tuple[str, int, str]]] = {
    "TEMPER": [
        ("Critic capsule", 5, "Jr NTR delivers a career-defining performance as Daya. The transition from an unapologetically greedy cop to a raging crusader in the courtroom is sheer cinematic adrenaline."),
        ("Audience review", 5, "Tarak's raw energy in the second half gave me literal goosebumps. Puri's hard-hitting dialogues hit straight in the chest, especially in the emotional pre-climax."),
        ("Film blog", 4, "Puri Jagannadh takes the familiar trope of police corruption and infuses it with unhinged swagger. The court scene stands as one of Telugu cinema's finest dramatic confrontations."),
        ("Critic capsule", 4, "An electrifying star vehicle anchored by NTR's unmatched screen presence. Posani Krishna Murali offers genuine heart and emotional gravity as constable Narayana Murthy."),
        ("Audience review", 5, "The interval bang completely flips the narrative. From comedy and swagger to unrelenting intensity, NTR carries the entire film on his shoulders."),
        ("Critic capsule", 3, "The first half relies too heavily on routine commercial eccentricities and formulaic romance, but the ferocious second hour redeems the film entirely."),
        ("Audience review", 4, "Mani Sharma's background score elevates every confrontation scene. Prakash Raj makes a formidable adversary who brings out the absolute best in Tarak."),
        ("Film blog", 5, "A brutally honest transformation story that does not sugarcoat its protagonist's initial flaws. The climax sacrifice feels tragic, shocking, and profoundly earned."),
        ("Critic capsule", 2, "While the courtroom monologue is undeniably stirring, the film's treatment of female characters in the earlier acts remains problematic and dated."),
        ("Audience review", 3, "Great dialogues and high-voltage acting, though the pacing in the romantic track with Kajal slows down an otherwise blistering crime drama."),
        ("Film blog", 4, "Daya is not a hero who plays by the rules; he is a broken man who realizes that redemption requires destroying his own comfort. Exceptional screenwriting by Vakkantham Vamsi."),
        ("Audience review", 5, "That iconic salute scene between Posani and NTR brought tears to everyone in the theatre. Pure emotion blended seamlessly with commercial power."),
        ("Critic capsule", 3, "Loud, intense, and occasionally chaotic, Temper succeeds primarily because Jr NTR refuses to dial down his ferocious commitment for even a second."),
        ("Audience review", 2, "The shift in tone after the interval is so jarring that it feels like two completely different films stitched together by an angry director."),
        ("Film blog", 4, "Puri Jagannadh's sharp punchlines crackle with cynicism before turning into righteous fury. It reinvented NTR's career and redefined modern Telugu mass cinema."),
        ("Critic capsule", 5, "Few mainstream Indian films transition into a discussion on judicial accountability and victim rights with this kind of unapologetic theatrical venom."),
        ("Audience review", 4, "The dance numbers show off NTR's supreme rhythm, but it is his voice modulation in the climax speech that lingers long after the credits roll."),
        ("Critic capsule", 2, "Heavy-handed moralizing at the finish cannot fully erase the unpalatable cynicism of the movie's first hour. An uneven experience."),
        ("Audience review", 5, "Saw it on first day first show in Hyderabad. The theater erupted during the climax. Daya is an unforgettable character in Telugu action cinema."),
        ("Film blog", 3, "Entertaining and intensely theatrical, though Puri's trademark rapid editing and repetitive henchmen fights test your patience in between dramatic high points."),
        ("Audience review", 5, "The chemistry between Posani and NTR represents the conscience of the movie. A powerful reminder that true cinema can inspire real emotional shock."),
        ("Critic capsule", 4, "A fiery, relentless action drama that proves commercial Telugu cinema can tackle harrowing social issues without abandoning its crowd-pleasing roots."),
        ("Audience review", 3, "Standard Puri template with dirty cops and beach romances, yet lifted to another league by NTR's unmatched expressive range and volcanic fury."),
        ("Film blog", 5, "Temper is a masterclass in star reinvention. It stripped away formulaic heroism and gave us an anti-hero whose redemption felt like a thunderbolt."),
    ],
    "RRR": [
        ("Critic capsule", 5, "A cinematic tsunami of pure unadulterated spectacle. S.S. Rajamouli orchestrates mythological heroism and kinetic choreography on a canvas that leaves Hollywood blockbusters in the dust."),
        ("Audience review", 5, "Naatu Naatu is pure joy incarnate. The speed, sync, and infectious energy between Ram Charan and Jr NTR had the entire auditorium dancing in the aisles."),
        ("Film blog", 5, "The interval sequence featuring wild predators exploding from the back of a cargo truck is easily one of the most audacious action set pieces ever committed to film."),
        ("Critic capsule", 5, "Rajamouli understands the emotional language of mass spectacle better than any living director. RRR delivers mythic grandeur backed by a deeply felt brotherly love."),
        ("Audience review", 5, "Ram Charan's introduction scene fighting off thousands of protestors single-handedly is an unbelievable feat of stunt coordination, grit, and visual storytelling."),
        ("Critic capsule", 4, "Unapologetically maximalist, exhilarating, and emotionally sincere. The sheer scale and imagination drown out any minor storytelling indulgences."),
        ("Audience review", 4, "Keeravani's thunderous musical score elevates every heartbeat. Dosti sets the soulful bond, while the battle anthems roar with primeval patriotic fire."),
        ("Film blog", 5, "Jr NTR's portrayal of Komaram Bheem combines childlike innocence with volcanic physical prowess. His emotional breakdown during the whipping scene is heartbreaking."),
        ("Critic capsule", 3, "Breathtaking in its kinetic high points, though the British caricatures lack any shred of nuance and the third act tilts toward unabashed patriotic melodrama."),
        ("Audience review", 5, "Three hours went by in a flash. The synergy between Charan and Tarak is once-in-a-generation magic. You believe in their friendship completely."),
        ("Film blog", 4, "A triumph of imaginative historical revisionism. It takes two real-life Indian revolutionaries who never met and turns their imaginary collision into an opera of fire and water."),
        ("Audience review", 5, "The piggyback tag-team combat in the climax prison escape had our whole theater screaming in disbelief. It takes comic-book team-ups to an art form."),
        ("Critic capsule", 4, "Sensory overload in the best possible way. Even when the CGI stretches the laws of physics, the emotional stakes remain rock-solid and human."),
        ("Audience review", 3, "Stunning action sequences and memorable music, though Alia Bhatt and Ajay Devgn feel somewhat shoehorned into an already overstuffed narrative."),
        ("Film blog", 5, "RRR achieved the impossible by breaking out globally not as a cultural curiosity, but as an undeniable masterclass in visceral visual storytelling."),
        ("Critic capsule", 2, "Relentlessly noisy and exhausting across three hours. The gravity-defying superhero physics strip away the genuine human struggle of anti-colonial resistance."),
        ("Audience review", 5, "The sheer craftsmanship on display from Senthil Kumar's dynamic cinematography to Srinivas Mohan's visual effects sets a brand new benchmark for Indian cinema."),
        ("Critic capsule", 3, "A grand spectacle with irresistible kinetic momentum, though it leaves little room for quiet contemplation or complex political subtext."),
        ("Audience review", 5, "Watched it three times on the big screen. The emotional payoff when Raju emerges as Alluri with the bow and arrow is unmatched euphoria."),
        ("Film blog", 4, "Rajamouli proves that sincere melodrama and peerless action choreography are not mutually exclusive. An exhilarating love letter to populist entertainment."),
        ("Audience review", 4, "The bridge rescue sequence in the first act establishes the core theme of brotherhood with astonishing visual clarity and zero unnecessary exposition."),
        ("Critic capsule", 5, "A towering achievement in populist world cinema. RRR reminds us why we fell in love with going to the movie theaters in the first place."),
        ("Audience review", 2, "Too long, too loud, and too melodramatic for my taste. The emotional beats feel manufactured under deafening orchestral music."),
        ("Film blog", 5, "Fire and water, brother against brother, nation against empire. RRR is pure mythmaking elevated to the stratosphere of global cinematic wonder."),
    ],
    "RYALASEEMA RAMANNA CHOWDARY": [
        ("Critic capsule", 4, "Mohan Babu delivers a commanding, authoritative performance as Ramanna Chowdary. His majestic dialogue delivery and authentic Rayalaseema accent anchor the entire narrative."),
        ("Audience review", 5, "A landmark rural faction drama from the early 2000s. Mohan Babu's screen presence in the white dhoti and mustache remains etched in the memories of Telugu movie lovers."),
        ("Film blog", 4, "Director Suresh Krissna brings his signature brisk pacing to a rural faction landscape, balancing heavy family drama with explosive mass dialogue confrontations."),
        ("Critic capsule", 3, "A quintessential rural melodrama that celebrates traditional village leadership. While the storyline follows familiar tropes, the theatrical acting keeps it compelling."),
        ("Audience review", 4, "Jayasudha's understated performance provides a magnificent contrast to Mohan Babu's thunderous baritone. Their veteran chemistry gives the film its moral center."),
        ("Audience review", 5, "Koti's songs were everywhere that year. The background score during the panchayat judgment sequences created electric theatrical moments."),
        ("Critic capsule", 3, "The faction feud premise was dominant in that era of Tollywood, but Ramanna Chowdary stands out for its strong emphasis on justice and non-violence over mindless bloodshed."),
        ("Film blog", 4, "The film tackles deep-rooted regional enmity in Seema districts with theatrical gravitas. Mohan Babu proves why he was titled the Dialogue King of Telugu cinema."),
        ("Critic capsule", 2, "Overtly loud and steeped in patriarchal savior tropes. The pacing sags heavily during the comedic interludes and standard romantic subplots."),
        ("Audience review", 3, "A nostalgic watch for 90s Telugu cinema fans. The second half gets predictable, but the dramatic confrontation between rival families delivers satisfying entertainment."),
        ("Film blog", 4, "Ramanna Chowdary's strict code of ethics makes him a memorable protagonist. The script treats the regional Rayalaseema ethos with genuine dignity and reverence."),
        ("Audience review", 5, "The scene where Ramanna stands in the assembly to defend his village's honor is pure goosebumps. No one delivers punch dialogues with the rhythm and impact of Mohan Babu."),
        ("Critic capsule", 3, "Suresh Krissna keeps the dramatic stakes high, though some of the supporting characters feel caricatured and the violence is occasionally excessive."),
        ("Audience review", 2, "Too dramatic and theatrical for modern sensibilities. The constant loud confrontations and weeping family members feel exhausting by the climax."),
        ("Film blog", 4, "An important milestone in early 2000s Telugu cinema's exploration of regional Rayalaseema identity, balancing mainstream heroism with deep cultural resonance."),
        ("Critic capsule", 4, "A powerful vehicle for Mohan Babu's formidable theatrical range. It combines folk charm, family sentiment, and high-octane rural conflict into an engaging package."),
        ("Audience review", 4, "Priya Raman and the supporting cast do complete justice to their roles. The village court judgment scenes remain classic Telugu cinema moments."),
        ("Critic capsule", 2, "The movie relies far too heavily on standard formulas of village honor, sacrifice, and predictable betrayals without offering any fresh narrative perspective."),
        ("Audience review", 5, "Watched this with my family multiple times during festival holidays. A heartfelt story about respecting our roots and standing up for the defenseless."),
        ("Film blog", 3, "While formulaic in its faction revenge structure, Mohan Babu's magnetic personality and resonant diction elevate the film above its contemporary peers."),
        ("Audience review", 4, "The dialogue delivery in the climax is legendary. Mohan Babu's command over language and pauses shows the caliber of golden-era Telugu character actors."),
        ("Critic capsule", 3, "Engaging rural drama with solid production values for its era, though it struggles to break free from well-worn faction action clichés."),
        ("Audience review", 3, "Good emotional depth in the relationship between husband and wife, but the villain tracks and rival family subplots feel repetitive after a while."),
        ("Film blog", 4, "A memorable entry in the Rayalaseema faction genre that chooses harmony over vengeance, anchored by one of Mohan Babu's most dignified performances."),
    ],
    "PARADISE": [
        ("Critic capsule", 5, "A masterclass in slow-burning psychological tension. Prasanna Vithanage transforms a scenic holiday into a searing indictment of middle-class entitlement and systemic inequality."),
        ("Audience review", 4, "Roshan Mathew and Darshana Rajendran are phenomenal as Keshav and Amritha. The subtle shifts in their relationship as crisis mounts feel terrifyingly real."),
        ("Film blog", 5, "Against the backdrop of the 2022 Sri Lankan economic collapse, Paradise exposes how fragile modern relationships are when stripped of privilege and comfort."),
        ("Critic capsule", 4, "Rajeev Ravi's naturalistic cinematography captures the lush beauty of Sri Lanka's central highlands while maintaining an undercurrent of claustrophobic dread."),
        ("Audience review", 4, "A quiet, devastating film that avoids melodramatic shortcuts. The tension builds organically from a stolen laptop into a moral catastrophe."),
        ("Critic capsule", 5, "Winner of the Kim Jiseok Award at Busan for good reason. Vithanage observes human arrogance and vulnerability with unsparing clarity and deep empathy."),
        ("Film blog", 4, "The film uses the Ramayana epic not as simple mythology, but as an ironic, haunting mirror to contemporary geopolitical arrogance and spousal betrayal."),
        ("Audience review", 3, "Deeply atmospheric and thought-provoking, though the deliberate arthouse pacing and sparse dialogue require patient, attentive viewing."),
        ("Critic capsule", 4, "Mahendra Perera's performance as the weary police sergeant Bandara is quietly brilliant. He embodies the exhaustion and casual brutality of an unraveling state."),
        ("Audience review", 2, "Too grim and slow for my taste. Very little happens in the first hour, and the ending leaves you feeling bitter and hollow rather than satisfied."),
        ("Film blog", 5, "Darshana Rajendran's eyes convey entire paragraphs of unspoken disappointment. Amritha's realization of her husband's moral cowardice is the true heart of the film."),
        ("Critic capsule", 3, "An intelligent, layered examination of class divide and tourism ethics, even if its central metaphor occasionally feels a bit too calculated."),
        ("Audience review", 4, "A chilling portrait of how quickly tourist privilege turns into authoritarian hostility when foreigners feel inconvenienced in a developing country."),
        ("Critic capsule", 2, "The pacing drags significantly in the middle act, and the escalating police interrogation scenes become overwhelmingly bleak and repetitive."),
        ("Film blog", 4, "K's evocative score enhances the simmering dread without ever manipulating the audience. A brilliant showcase for independent South Asian cinema."),
        ("Audience review", 5, "The final shot stayed with me for days. Paradise does not give you easy answers; it forces you to confront your own complicity in social oppression."),
        ("Critic capsule", 5, "Taut, economical storytelling at its finest. At just 93 minutes, Paradise achieves more philosophical depth than films twice its length."),
        ("Audience review", 3, "Compelling character study and top-notch acting from both lead actors, though the climax feels somewhat abrupt and deeply unsettling."),
        ("Film blog", 4, "Prasanna Vithanage refuses to sensationalize the Sri Lankan crisis. The fuel queues, blackouts, and quiet desperation form a palpably authentic environment."),
        ("Critic capsule", 4, "A brilliant deconstruction of the male ego. Keshav's desperation to complete his film deal blinds him to basic human compassion and marital decency."),
        ("Audience review", 5, "One of the best South Asian films of recent years. Honest, uncompromising, and visually magnificent. A triumph of collaborative cinema."),
        ("Critic capsule", 3, "Technically polished and exceptionally acted, though its pessimistic worldview offers little catharsis or emotional relief for the viewer."),
        ("Audience review", 4, "The contrast between the luxurious secluded villa and the suffering locals outside creates a powerful moral tension that never lets up."),
        ("Film blog", 5, "Paradise is a rare cinematic gem that works simultaneously as a thrilling domestic mystery, a sociological critique, and a poetic tragedy."),
    ],
}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for title, reviews in REVIEWS.items():
        meta = META[title]
        for index, (source, rating, text) in enumerate(reviews, start=1):
            slug = title.lower().replace(" ", "-")
            rows.append(
                {
                    "review_id": f"{slug}-{index:02d}",
                    "title": title,
                    "year": meta["year"],
                    "director": meta["director"],
                    "genre": meta["genre"],
                    "runtime": meta["runtime"],
                    "accent": meta["accent"],
                    "blurb": meta["blurb"],
                    "source": source,
                    "rating": rating,
                    "text": text,
                }
            )

    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} reviews across {len(REVIEWS)} titles to {OUT}")


if __name__ == "__main__":
    main()
