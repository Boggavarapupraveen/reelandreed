"""Build the curated review corpus used by the dashboard.

The corpus is deliberately small, transparent, and dependency-free. Each row is an
anonymised review excerpt written for this teaching project; no real critic quote is
attributed to a named person. Run from the project root:

    python scripts/build_corpus.py
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reviews.csv"

# (source, star rating, review text)
REVIEWS: dict[str, list[tuple[str, int, str]]] = {
    "The Shawshank Redemption": [
        ("Critic capsule", 5, "A quietly devastating prison drama that earns every ounce of its hope. The friendship between Andy and Red is the emotional spine, and the final beach scene still feels like a release."),
        ("Audience review", 5, "I put this on whenever I need to believe that patience matters. The pacing is unhurried, but never boring."),
        ("Critic capsule", 5, "Morgan Freeman's narration could read a grocery list and make it profound. Paired with Robbins' restrained performance, the film is close to perfect."),
        ("Audience review", 5, "The tunnel escape reveal is one of cinema's great payoffs. Decades later, the practical effects and patient setup still land."),
        ("Film blog", 5, "A story about institutional cruelty that never wallows. It finds small acts of dignity and makes them enormous."),
        ("Audience review", 4, "The supporting cast is stacked, but the movie never loses focus. Every subplot circles back to freedom and friendship."),
        ("Critic capsule", 3, "Technically accomplished and well acted, though the film's earnestness can feel a little too tidy. I admire it more than I love it."),
        ("Audience review", 3, "A solid, old-fashioned crowd-pleaser. The middle stretch drags, but the ending is undeniably effective."),
        ("Critic capsule", 2, "The film is so determined to be uplifting that it sands down the brutality of prison life. It is a fairy tale with a life sentence."),
        ("Film blog", 5, "The scene where the prisoners hear Mozart over the loudspeakers is pure cinema. In two minutes it explains why art matters inside a cage."),
        ("Audience review", 5, "Brooks' storyline broke me. The film understands that release can be another kind of sentence."),
        ("Critic capsule", 3, "Handsome production, strong performances, familiar message. It is a very good film that has somehow been crowned a flawless one."),
        ("Audience review", 5, "I avoided it for years because of the hype. The hype is right. A patient, humane story with an ending that feels earned."),
        ("Critic capsule", 2, "Too long and too pleased with its own symbolism. The prison is a metaphor, we get it."),
        ("Audience review", 5, "The friendship is the point, not the escape. That is why the final reunion works so well."),
        ("Critic capsule", 5, "Thomas Newman's score is restrained and beautiful. It never tells you how to feel, which makes the feelings land harder."),
        ("Film blog", 4, "A rare adaptation that improves on its source by tightening the focus and letting the faces carry the story."),
        ("Audience review", 3, "The first act is gripping, the second is comfortable, the third is pure wish fulfillment. Whether that is a flaw depends on what you want."),
        ("Critic capsule", 5, "Bob Gunton's warden is a wonderfully loathsome villain. The institutional hypocrisy is the real monster."),
        ("Audience review", 5, "Watched it with my teenage nephew. He was silent for the last twenty minutes, then asked to watch it again. That is the review."),
        ("Critic capsule", 2, "The movie treats Andy's intelligence as a magic trick. Every problem is solved by a convenient skill, which drains the tension."),
        ("Audience review", 5, "The get busy living or get busy dying line is famous for a reason. It is the thesis of a film that earns its optimism."),
        ("Critic capsule", 3, "A dependable five-star movie for people who only watch three movies a year. Not a criticism, exactly."),
        ("Film blog", 5, "The rain-soaked escape is iconic, but the quiet moments in the library matter just as much. A film about keeping your mind free when your body is not."),
    ],
    "The Dark Knight": [
        ("Critic capsule", 5, "Ledger's Joker is a force of nature, but the film around him is just as strong. A crime epic that happens to wear a cape."),
        ("Audience review", 5, "The interrogation scene is two actors at the top of their game. No score, no effects, just pure dread."),
        ("Film blog", 4, "Nolan turns Gotham into a city with real institutions and real rot. The moral questions are heavier than the action, which is the point."),
        ("Critic capsule", 5, "A superhero sequel that refuses to be comforting. The ferry sequence is a genuine ethical stress test, not a set piece."),
        ("Audience review", 2, "Grim, loud, and endlessly self-serious. The film mistakes darkness for depth and never lets anyone breathe."),
        ("Audience review", 4, "The opening bank heist is a masterclass in escalation. It tells you everything about the Joker before he says a word."),
        ("Critic capsule", 5, "Eckhart's Harvey Dent is the tragedy at the centre. His fall gives the film a weight most blockbusters never attempt."),
        ("Audience review", 3, "The plot is ambitious but tangled. I needed a whiteboard for the second act and a nap for the third."),
        ("Film blog", 5, "The film understands that Batman is not the most interesting character in his own story. Gotham is."),
        ("Critic capsule", 2, "The Harvey Dent arc is rushed into a final act that feels like two movies stapled together. Great villain, messy structure."),
        ("Audience review", 5, "The score by Hans Zimmer and James Newton Howard tightens every scene like a wire. That low horn motif is unforgettable."),
        ("Audience review", 3, "Impressive set pieces and a superb villain, but the female characters are written as plot devices."),
        ("Critic capsule", 4, "A dense, confident blockbuster with a bleak view of human nature. It is not fun, exactly, but it is gripping."),
        ("Film blog", 5, "The final choice about the ferry is the film's thesis: people are capable of decency, even when no one is watching."),
        ("Audience review", 2, "The action editing is incoherent. I spent half the chase wondering who was hitting whom."),
        ("Critic capsule", 3, "A very good crime film trapped inside a very long superhero film. The pacing sags whenever the Joker leaves the room."),
        ("Audience review", 5, "Rachel's letter and the final montage give the movie an ache that stays with you. It earns its sombre ending."),
        ("Critic capsule", 5, "Every performance is calibrated to the film's moral register. Even the smaller roles feel lived in."),
        ("Audience review", 2, "It is relentlessly grim and strangely humourless. A little levity would have made the darkness hit harder."),
        ("Film blog", 4, "The film's architecture is extraordinary: three villain arcs, one city, and a single question about what order is worth."),
        ("Audience review", 3, "Solid entertainment with an all-time great performance. I just do not think it is the masterpiece people claim."),
        ("Critic capsule", 5, "A rare blockbuster that trusts its audience to sit with ambiguity. The ending is a cost, not a victory."),
        ("Audience review", 4, "The Batpod chase is still thrilling, and the practical effects give the action real weight."),
        ("Film blog", 5, "The Dark Knight changed what a comic-book movie could be. Its shadow is long because its ideas are genuinely large."),
    ],
    "Inception": [
        ("Critic capsule", 5, "A rare blockbuster built around an original idea and executed with total conviction. The dream logic is intricate without being impenetrable."),
        ("Audience review", 4, "The hallway fight and the folding city are still jaw-dropping. I just wish the emotional core had a little more room to breathe."),
        ("Film blog", 5, "Nolan turns exposition into action. The rules of the dream machine are delivered while the film is already sprinting, and it works."),
        ("Audience review", 2, "A cold puzzle box that keeps explaining itself. By the third layer I stopped caring and started checking the runtime."),
        ("Critic capsule", 3, "Technically astonishing, emotionally distant. The film is more interested in its own mechanics than in Cobb's grief."),
        ("Audience review", 4, "The final spinning top is a perfect ending because it is about the character, not the answer. I do not need the internet to tell me what happened."),
        ("Critic capsule", 5, "Zimmer's score is a tidal wave of brass and ticking clocks. It makes the dream layers feel physically heavy."),
        ("Audience review", 2, "The dialogue is mostly characters telling each other the plot. It is a heist movie wearing a philosophy costume."),
        ("Critic capsule", 3, "A dazzling construction with a hollow centre. I admired the craft more than I felt the stakes."),
        ("Audience review", 4, "The ensemble is absurdly good. Tom Hardy steals every scene he is in, and the hotel sequence is pure fun."),
        ("Critic capsule", 5, "The film's real subject is guilt, not dreams. Once you see Mal as Cobb's conscience, every action beat becomes a therapy session."),
        ("Audience review", 2, "The sound mix is a problem. I could barely hear the dialogue over the score, and the plot depends on dialogue."),
        ("Critic capsule", 4, "A bold, beautiful machine of a movie. It does not always connect emotionally, but it never stops inventing."),
        ("Audience review", 3, "Impressive on a first watch, exhausting on a second. The film's cleverness starts to feel like homework."),
        ("Film blog", 5, "The van falling in slow motion while the other layers race forward is one of the great set pieces of the 2010s. Editing as spectacle."),
        ("Audience review", 2, "The female lead exists only to be a memory and a obstacle. For a film about the mind, it has a very narrow imagination."),
        ("Critic capsule", 4, "A heist film with the structure of a symphony. The cross-cutting between layers is precise, propulsive, and genuinely original."),
        ("Audience review", 3, "There is a great ninety-minute movie somewhere in here. The extra hour is mostly people explaining the rules."),
        ("Critic capsule", 5, "The zero-gravity hotel corridor remains a practical-effects miracle. It is the kind of image that reminds you why cinemas exist."),
        ("Audience review", 1, "Loud, confusing, and pleased with itself. I left with a headache and no feeling for any of the characters."),
        ("Film blog", 4, "The film is a magic trick about magic tricks: the more you look for the seams, the more you want to believe."),
        ("Audience review", 3, "A very good first date movie because you can spend dinner arguing about the ending. As a story, it is a little thin."),
        ("Critic capsule", 4, "Cobb's grief gives the mechanics a pulse. The film is colder than it thinks, but the final reunion is genuinely moving."),
        ("Audience review", 5, "I have seen it five times and still notice new details in the background. A dense, rewarding blockbuster that treats viewers like adults."),
    ],
    "La La Land": [
        ("Critic capsule", 5, "A bittersweet love letter to ambition and the people who get left behind. The final sequence is a masterclass in what might have been."),
        ("Audience review", 5, "The opening freeway number is pure joy. Chazelle understands that a musical should feel like it could burst out of the pavement."),
        ("Audience review", 2, "Beautiful to look at, but the songs are forgettable and the characters are thin. Style over substance."),
        ("Film blog", 4, "Gosling and Stone have effortless chemistry. The film works best when it stops performing and lets them be quietly uncertain."),
        ("Critic capsule", 3, "A gorgeously mounted confection that has less to say than it thinks. Still, that ending is undeniable."),
        ("Audience review", 5, "The planetarium dance made me feel like a kid watching old Hollywood. A romantic, melancholy, completely lovely film."),
        ("Audience review", 2, "A movie about jazz that seems to hate jazz. The protagonist is a pretentious bore and the film never challenges him."),
        ("Critic capsule", 4, "The colour palette is extraordinary, and the camera moves with real musicality. A few numbers outstay their welcome, but the whole is intoxicating."),
        ("Audience review", 3, "The first half is magical, the second half is a long conversation about compromise. I wanted more dancing and less moping."),
        ("Film blog", 5, "The epilogue is one of the most moving things mainstream cinema has produced this century. A whole life in five minutes."),
        ("Critic capsule", 1, "An empty nostalgia exercise with a thin script and a baffling central romance. The film is in love with its own references."),
        ("Audience review", 4, "Not every song lands, but the ones that do are wonderful. City of Stars has been stuck in my head for a week."),
        ("Audience review", 2, "The leads can sing, but they cannot sell the fairy tale. I felt the sadness of the ending without ever believing the love."),
        ("Critic capsule", 4, "A sincere, risky studio musical. It does not always work, but when it does, it is transportive."),
        ("Audience review", 3, "Gorgeous, charming, and a little hollow. I enjoyed it while it was on and forgot about it by dinner."),
        ("Film blog", 5, "The film understands that love and ambition can both be real and still incompatible. That is a braver story than a simple happy ending."),
        ("Audience review", 2, "The jazz gatekeeping subplot is unbearable. A white protagonist lectures a Black musician about authenticity, and the film agrees with him."),
        ("Critic capsule", 4, "The choreography, costumes, and lighting are a loving tribute to a bygone studio system. The melancholy keeps it from becoming pastiche."),
        ("Audience review", 3, "A lovely diversion with two appealing stars. It is not the second coming of the movie musical, and that is fine."),
        ("Film blog", 5, "The final look between Mia and Seb contains an entire marriage, a career, and a regret. That is star power and direction working as one."),
        ("Critic capsule", 2, "The film keeps insisting on its own magic. Real magic does not need to point at itself for two hours."),
        ("Audience review", 4, "The winter-to-spring structure is elegant, and the bittersweet ending respects the choices these people made."),
        ("Critic capsule", 3, "A stylish, well-acted experiment that is more interesting as a cultural artefact than as a story. The soundtrack is the best part."),
        ("Audience review", 1, "I found it smug and emotionally manipulative. The film wants credit for being sad without doing the work of earning it."),
    ],
    "Cats": [
        ("Critic capsule", 2, "A bizarre, expensive misfire. The digital fur is unsettling, the songs blur together, and the plot is a scrapbook of nonsense."),
        ("Audience review", 1, "I have never been so confused by a movie's sense of scale. The cats are human-sized, the sets are giant, and none of it matters."),
        ("Film blog", 2, "There is a fascinating disaster buried in here. The commitment of the performers is real, which makes the material's emptiness stranger."),
        ("Audience review", 5, "Unironically delightful. It is theatrical, silly, and completely committed to its own weird dream logic. I had a great time."),
        ("Audience review", 2, "The visual effects make my eyes tired. Every cat looks like a snapped rubber glove with a wig."),
        ("Critic capsule", 3, "A chaotic curiosity. It is not good in any conventional sense, but it is never boring, and that counts for something."),
        ("Audience review", 1, "A relentless parade of unfinished CGI and songs with no melody. I left before the end and I regret nothing."),
        ("Film blog", 2, "The film strips away the stage show's intimacy and replaces it with digital noise. A musical without rhythm or wonder."),
        ("Audience review", 4, "So strange that it loops back around to charming. The Jellicle Ball is a hallucination, but I was smiling."),
        ("Critic capsule", 2, "The choreography is energetic, the production design is enormous, and the whole thing feels like a fever dream dictated to a tax accountant."),
        ("Audience review", 1, "The close-ups of the cat faces will haunt me. Why do their hands have fur and their feet have shoes?"),
        ("Critic capsule", 3, "A genuinely baffling artefact of studio hubris. I cannot recommend it, but I also cannot forget it."),
        ("Audience review", 2, "Taylor Swift's number is the only time the film wakes up. Then it goes back to sleep for another hour."),
        ("Film blog", 4, "A cult classic in the making. Watch it with friends, lower your expectations, and embrace the chaos."),
        ("Audience review", 1, "The songs are forgettable, the story is nonexistent, and the visual style is deeply unpleasant. A complete failure."),
        ("Critic capsule", 2, "The film has no idea what tone it wants. It lurches from camp to sincerity without ever finding a rhythm."),
        ("Audience review", 1, "I did not think a movie about cats could feel this joyless. It is a two-hour commercial for nothing."),
        ("Film blog", 2, "The stage show's magic came from bodies in a room. This version replaces presence with pixels and loses the point entirely."),
        ("Audience review", 1, "The editing is frantic, the framing is claustrophobic, and the dance sequences are chopped into confetti. Unwatchable."),
        ("Critic capsule", 4, "An audacious, unclassifiable mess that I found weirdly endearing. It fails spectacularly, but it fails with style."),
        ("Audience review", 2, "The cast is talented and utterly stranded. Judi Dench deserves a better send-off than a digital fur coat."),
        ("Critic capsule", 1, "A joyless, shapeless adaptation that misunderstands everything that made the stage musical work. One of the year's worst."),
        ("Audience review", 1, "The plot is a talent show for cats, and the prize is death. I wish I were joking."),
        ("Audience review", 3, "A wild piece of studio history. I would rather read about how it got made than watch it again, but I am glad it exists."),
    ],
}

META = {
    "The Shawshank Redemption": {
        "year": 1994,
        "director": "Frank Darabont",
        "genre": "Prison drama",
        "runtime": "142 min",
        "accent": "#C9A227",
        "blurb": "Hope, friendship, and a very long game inside Shawshank State Penitentiary.",
    },
    "The Dark Knight": {
        "year": 2008,
        "director": "Christopher Nolan",
        "genre": "Crime thriller",
        "runtime": "152 min",
        "accent": "#2E6F95",
        "blurb": "Gotham's moral fault lines crack open when the Joker arrives.",
    },
    "Inception": {
        "year": 2010,
        "director": "Christopher Nolan",
        "genre": "Sci-fi heist",
        "runtime": "148 min",
        "accent": "#6C5CE7",
        "blurb": "A thief who steals ideas must plant one — and face the dream he left behind.",
    },
    "La La Land": {
        "year": 2016,
        "director": "Damien Chazelle",
        "genre": "Musical romance",
        "runtime": "128 min",
        "accent": "#D94F70",
        "blurb": "Two dreamers fall in love in a Los Angeles that keeps asking them to choose.",
    },
    "Cats": {
        "year": 2019,
        "director": "Tom Hooper",
        "genre": "Musical fantasy",
        "runtime": "110 min",
        "accent": "#8A7B5A",
        "blurb": "A digital-fur fever dream where the Jellicle cats compete for a new life.",
    },
}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for title, reviews in REVIEWS.items():
        meta = META[title]
        for index, (source, rating, text) in enumerate(reviews, start=1):
            rows.append(
                {
                    "review_id": f"{title.lower().replace(' ', '-')}-{index:02d}",
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
