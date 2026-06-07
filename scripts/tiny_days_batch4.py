"""Batch 4 tiny-animal episodes (ep20-26) — 7 new animals + distinct arcs, continuing the
1-video/day phase (schedule 2026-06-19+). Mix real + fantasy. Merged by tiny_produce.
scenes = (image_prompt_en, motion_prompt_en) x 7. STYLE appended by tiny_produce.
"""

EPISODES_B4 = {
    # 🦉 baby owl — NIGHT LIBRARY
    "ep20": {
        "title": "Thư viện đêm của cú con tí hon", "slug": "tiny_library_owl", "kind": "real",
        "music": "output/tiny_animals/_bgm/night_library.mp3",
        "entity": {"name": "tiny owl", "entity_type": "creature",
                   "image_prompt": ("a tiny fluffy baby owl, soft brown and cream feathers, huge round amber "
                                    "eyes, tiny beak, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny fluffy baby owl perched on a stack of tiny books in a cozy candle-lit library, warm macro",
             "a tiny owl on a stack of books blinking slowly, candle flicker, slow cozy"),
            ("a tiny baby owl opening a tiny book with its wing, warm cozy library macro",
             "a tiny owl nudging a tiny book open with its wing, slow gentle cozy"),
            ("a tiny baby owl beside a tiny glowing candle and an open book, warm cozy macro",
             "a tiny owl gazing at a tiny candle flame, warm glow on feathers, slow calm"),
            ("a tiny baby owl turning a page of a tiny book, cozy library macro",
             "a tiny owl gently turning a tiny page, head tilting, slow cozy"),
            ("a tiny baby owl beside a tiny cup of tea with steam, cozy library macro",
             "steam rising from a tiny tea cup beside a calm owl, slow warm"),
            ("a tiny baby owl yawning sleepily over an open book, warm cozy macro",
             "a tiny owl yawning wide, eyes drooping, slow sleepy"),
            ("a tiny baby owl asleep nestled on an open book, candle low, peaceful macro",
             "a tiny owl sleeping on a book, feathers settling, candle glow low, very slow peaceful"),
        ],
    },
    # 🦌 baby fawn — SPRING MEADOW MORNING
    "ep21": {
        "title": "Sáng xuân hái hoa của hươu con tí hon", "slug": "tiny_meadow_fawn", "kind": "real",
        "music": "output/tiny_animals/_bgm/spring_meadow.mp3",
        "entity": {"name": "tiny fawn", "entity_type": "creature",
                   "image_prompt": ("a tiny baby deer fawn, soft tan fur with white spots, big gentle dark eyes, "
                                    "tiny hooves, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny spotted baby fawn waking up in soft spring grass with wildflowers, morning light, macro",
             "a tiny fawn waking and blinking in dewy grass, soft morning light, slow gentle"),
            ("a tiny baby fawn stepping carefully through tiny wildflowers, spring macro",
             "a tiny fawn stepping gently among little flowers, ears twitching, slow cozy"),
            ("a tiny baby fawn sniffing a tiny flower, spring morning macro",
             "a tiny fawn leaning in to sniff a tiny flower, nose wiggling, slow tender"),
            ("a tiny baby fawn with a tiny flower crown on its head, spring macro",
             "a tiny fawn wearing a little flower crown, looking up, slow sweet"),
            ("a tiny baby fawn drinking a dewdrop from a leaf, spring morning macro",
             "a tiny fawn sipping a dewdrop off a leaf, slow gentle"),
            ("a tiny baby fawn lying among soft wildflowers, content, spring macro",
             "a tiny fawn folding down into the flowers, content, slow peaceful"),
            ("a tiny baby fawn asleep in a bed of wildflowers, warm light, peaceful macro",
             "a tiny fawn sleeping among flowers, petals drifting, very slow peaceful"),
        ],
    },
    # 🐨 baby koala — LAZY EUCALYPTUS DAY
    "ep22": {
        "title": "Ngày lười ôm cây của koala con tí hon", "slug": "tiny_tree_koala", "kind": "real",
        "music": "output/tiny_animals/_bgm/eucalyptus_nap.mp3",
        "entity": {"name": "tiny koala", "entity_type": "creature",
                   "image_prompt": ("a tiny baby koala, soft grey fluffy fur, big fluffy ears, round black nose, "
                                    "sleepy dark eyes, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny fluffy baby koala hugging a tiny eucalyptus branch, soft warm light, cozy macro",
             "a tiny koala hugging a little branch, blinking sleepily, slow cozy"),
            ("a tiny baby koala nibbling a tiny eucalyptus leaf, cozy macro",
             "a tiny koala slowly nibbling a eucalyptus leaf, slow content"),
            ("a tiny baby koala doing a big sleepy yawn while hugging a branch, cozy macro",
             "a tiny koala yawning wide hugging the branch, slow sleepy"),
            ("a tiny baby koala slowly climbing a tiny branch, cozy macro",
             "a tiny koala climbing a branch slowly, one paw at a time, very slow"),
            ("a tiny baby koala snuggled into the fork of a tiny tree, cozy macro",
             "a tiny koala settling into the tree fork, getting comfy, slow cozy"),
            ("a tiny baby koala being gently petted on the head, content, cozy macro",
             "a gentle fingertip stroking a tiny koala's head, eyes closing, slow tender"),
            ("a tiny baby koala asleep hugging a branch, peaceful macro",
             "a tiny koala sleeping hugging the branch, breathing slow, very slow peaceful"),
        ],
    },
    # 🐢 baby turtle — TINY GARDEN STROLL
    "ep23": {
        "title": "Dạo vườn tí hon của rùa con", "slug": "tiny_garden_turtle", "kind": "real",
        "music": "output/tiny_animals/_bgm/garden_stroll.mp3",
        "entity": {"name": "tiny turtle", "entity_type": "creature",
                   "image_prompt": ("a tiny baby turtle, smooth green-brown shell, sweet little face, big dark "
                                    "eyes, tiny legs, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny baby turtle poking its head out of its shell in a lush tiny garden, soft light, macro",
             "a tiny turtle slowly poking its head out, blinking, soft garden light, very slow"),
            ("a tiny baby turtle crawling across soft green moss, tiny garden macro",
             "a tiny turtle crawling slowly over moss, tiny legs moving, very slow cozy"),
            ("a tiny baby turtle nibbling a tiny strawberry, lush garden macro",
             "a tiny turtle taking slow bites of a tiny strawberry, slow content"),
            ("a tiny baby turtle sheltering under a tiny mushroom, cozy garden macro",
             "a tiny turtle tucked under a little mushroom, looking out, slow calm"),
            ("a tiny baby turtle under gentle dewdrops dripping from a leaf, garden macro",
             "soft dewdrops dripping onto a tiny turtle's shell, slow gentle"),
            ("a tiny baby turtle slowly tucking back into its cozy shell, garden macro",
             "a tiny turtle slowly drawing into its shell, content, very slow"),
            ("a tiny baby turtle asleep half-tucked in its shell on soft moss, peaceful macro",
             "a tiny turtle sleeping on moss, gentle breathing, very slow peaceful"),
        ],
    },
    # 🦊✨ baby kitsune — FLOATING LANTERN NIGHT
    "ep24": {
        "title": "Đêm đèn lồng của hồ ly con tí hon", "slug": "tiny_lantern_kitsune", "kind": "fantasy",
        "music": "output/tiny_animals/_bgm/lantern_night.mp3",
        "entity": {"name": "tiny kitsune", "entity_type": "creature",
                   "image_prompt": ("a tiny baby kitsune fox spirit, soft white-and-orange fur with two fluffy "
                                    "tails, big amber eyes, tiny paws, faint warm glow, palm-sized, adorable fantasy, photorealistic")},
        "scenes": [
            ("a tiny baby kitsune standing by a dark calm stream at night, soft warm glow, fantasy macro",
             "a tiny kitsune by a night stream, tails swaying, faint glow, slow gentle"),
            ("a tiny baby kitsune gently pushing a tiny paper lantern onto the water, fantasy macro",
             "a tiny kitsune nudging a tiny glowing lantern onto the stream, slow tender"),
            ("a tiny glowing paper lantern drifting on water beside a tiny kitsune, fantasy macro",
             "a tiny lantern drifting away glowing warm, reflection rippling, slow magical"),
            ("a tiny baby kitsune with its two tails softly glowing, night fantasy macro",
             "a tiny kitsune's tails glowing softly, warm light pulsing, slow magical"),
            ("a tiny baby kitsune surrounded by many floating glowing lanterns, fantasy macro",
             "many tiny lanterns drifting around a calm kitsune, soft glow, slow dreamy"),
            ("a tiny baby kitsune gazing up at the moon among lanterns, fantasy macro",
             "a tiny kitsune looking up at the moon, lanterns drifting, slow serene"),
            ("a tiny baby kitsune curled asleep by the glowing lanterns, peaceful fantasy macro",
             "a tiny kitsune sleeping curled up, tails glowing faintly, very slow peaceful"),
        ],
    },
    # 🦝 baby raccoon — WASHING TINY TREASURES (ASMR)
    "ep25": {
        "title": "Rửa kho báu tí hon của gấu mèo con", "slug": "tiny_wash_raccoon", "kind": "real",
        "music": "output/tiny_animals/_bgm/washing_asmr.mp3",
        "entity": {"name": "tiny raccoon", "entity_type": "creature",
                   "image_prompt": ("a tiny baby raccoon, soft grey fur with black mask markings, tiny nimble "
                                    "paws, big curious dark eyes, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny baby raccoon holding a tiny basket of little trinkets, cozy warm macro",
             "a tiny raccoon clutching a tiny basket of trinkets, curious, slow cozy"),
            ("a tiny baby raccoon dipping a tiny shiny bead into a small bowl of water, cozy macro",
             "a tiny raccoon dipping a bead into water, paws working, gentle ripples, slow"),
            ("a tiny baby raccoon scrubbing a tiny pebble with its paws, cozy ASMR macro",
             "a tiny raccoon rubbing a tiny pebble between its paws, slow satisfying"),
            ("a tiny baby raccoon lining up tiny clean beads in a row, cozy macro",
             "a tiny raccoon carefully placing tiny beads in a row, slow careful"),
            ("a tiny baby raccoon admiring its sparkling tiny treasures, cozy macro",
             "a tiny raccoon turning a sparkling bead in the light, eyes wide, slow happy"),
            ("a tiny baby raccoon drying its little treasures with a soft cloth, cozy macro",
             "a tiny raccoon patting treasures dry with a tiny cloth, slow gentle"),
            ("a tiny baby raccoon asleep hugging its basket of treasures, peaceful macro",
             "a tiny raccoon sleeping hugging its basket, content, very slow peaceful"),
        ],
    },
    # 🌙🐇 moon rabbit — POUNDING MOCHI UNDER THE MOON
    "ep26": {
        "title": "Giã mochi dưới trăng của thỏ mặt trăng tí hon", "slug": "tiny_mochi_moonrabbit", "kind": "fantasy",
        "music": "output/tiny_animals/_bgm/moon_mochi.mp3",
        "entity": {"name": "tiny moon rabbit", "entity_type": "creature",
                   "image_prompt": ("a tiny moon rabbit, soft silver-white fur with a faint moonlit glow, long "
                                    "ears, big gentle eyes, palm-sized, adorable fantasy, photorealistic")},
        "scenes": [
            ("a tiny glowing silver moon rabbit beside a tiny wooden mortar under a big bright moon, fantasy macro",
             "a tiny moon rabbit standing by a tiny mortar, moon glowing behind, slow serene"),
            ("a tiny moon rabbit lifting a tiny mallet to pound rice dough, moonlit fantasy macro",
             "a tiny moon rabbit raising and lowering a tiny mallet rhythmically, slow steady"),
            ("a tiny moon rabbit shaping soft white mochi with its paws, moonlit macro",
             "a tiny moon rabbit patting and shaping soft mochi, slow gentle"),
            ("a tiny moon rabbit dusting a tiny mochi ball with powder, fantasy macro",
             "a tiny moon rabbit sprinkling soft powder over mochi, slow tender"),
            ("a tiny moon rabbit taking a happy bite of a tiny mochi, moonlit macro",
             "a tiny moon rabbit nibbling a soft mochi, cheeks puffing, slow joyful"),
            ("a tiny moon rabbit content with a full belly under the moon, fantasy macro",
             "a tiny moon rabbit patting its full belly under the moon, slow content"),
            ("a tiny moon rabbit asleep beside the mortar under the glowing moon, peaceful fantasy macro",
             "a tiny moon rabbit sleeping under the moon, fur glowing faintly, very slow peaceful"),
        ],
    },
}
