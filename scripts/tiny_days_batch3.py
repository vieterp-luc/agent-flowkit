"""Batch 3 tiny-animal episodes (ep13-19) — 7 new animals + distinct arcs for the
1-video/day phase. Mix real + fantasy. Same schema as tiny_days; merged by tiny_produce.
scenes = (image_prompt_en, motion_prompt_en) x 7. STYLE appended by tiny_produce.
"""

EPISODES_B3 = {
    # 🐧 baby penguin — FIRST SWIM LESSON
    "ep13": {
        "title": "Bài học bơi đầu tiên của chim cánh cụt tí hon", "slug": "tiny_swim_penguin", "kind": "real",
        "music": "output/tiny_animals/_bgm/penguin_splash.mp3",
        "entity": {"name": "tiny penguin", "entity_type": "creature",
                   "image_prompt": ("a tiny fluffy baby penguin, soft grey down with a white belly, "
                                    "tiny orange beak and feet, big dark round eyes, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny fluffy baby penguin standing on a person's palm beside a tiny pool, cozy warm light, macro",
             "a tiny penguin looking curiously at the water, tilting its head, slow gentle cozy"),
            ("a tiny baby penguin dipping one foot into a tiny pool of water, hesitant and cute, macro",
             "a tiny penguin dipping a toe into water then pulling back, ripples, slow gentle"),
            ("a tiny baby penguin sliding belly-first into shallow clear water, gentle splash, cozy macro",
             "a tiny penguin sliding into shallow water, soft splash and ripples, slow playful"),
            ("a tiny baby penguin paddling happily in tiny clear water, cozy macro",
             "a tiny penguin paddling its little feet in the water, happy, slow cozy"),
            ("a tiny baby penguin nibbling a tiny fish from fingertips, cozy macro",
             "a tiny penguin gently taking a tiny fish, beak nibbling, slow tender"),
            ("a tiny baby penguin being gently towel-dried, down fluffing up, warm cozy macro",
             "a soft towel gently drying a tiny penguin, down puffing up, slow cozy"),
            ("a tiny baby penguin asleep on a soft cushion, content, peaceful macro",
             "a tiny penguin sleeping on a cushion, belly gently rising, very slow peaceful"),
        ],
    },
    # 🐼 red panda cub — SNOW DAY
    "ep14": {
        "title": "Ngày tuyết đầu tiên của gấu trúc đỏ tí hon", "slug": "tiny_snow_redpanda", "kind": "real",
        "music": "output/tiny_animals/_bgm/snowy_day.mp3",
        "entity": {"name": "tiny red panda", "entity_type": "creature",
                   "image_prompt": ("a tiny red panda cub, soft russet-red fur, cream face markings, "
                                    "fluffy ringed tail, big dark eyes, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny red panda cub in cupped hands watching the first snowflakes fall, cozy winter macro",
             "a tiny red panda watching snowflakes drift down, eyes wide, slow gentle cozy"),
            ("a tiny red panda cub reaching up to catch a snowflake on its nose, cute winter macro",
             "a tiny red panda reaching up as a snowflake lands on its nose, slow sweet"),
            ("a tiny red panda cub patting a tiny snowball with its paws, snowy cozy macro",
             "a tiny red panda patting a little snowball, paws pressing softly, slow playful"),
            ("a tiny red panda cub sliding down a tiny snowy slope, playful winter macro",
             "a tiny red panda sliding down a little snow slope, fluffy tail trailing, slow playful"),
            ("a tiny red panda cub warming up by a tiny fireplace, snow melting off fur, cozy macro",
             "a tiny red panda by a warm fire, fur drying, firelight flicker, slow cozy"),
            ("a tiny red panda cub beside a tiny cup of warm cocoa with steam, cozy macro",
             "steam rising from a tiny cocoa cup beside a content red panda, slow warm"),
            ("a tiny red panda cub curled asleep in a warm blanket, peaceful macro",
             "a tiny red panda sleeping curled in a blanket, tail wrapped, very slow peaceful"),
        ],
    },
    # 🦅✨ baby griffin — FIRST FLIGHT
    "ep15": {
        "title": "Chuyến bay đầu tiên của griffin con tí hon", "slug": "tiny_flight_griffin", "kind": "fantasy",
        "music": "output/tiny_animals/_bgm/first_flight.mp3",
        "entity": {"name": "tiny griffin", "entity_type": "creature",
                   "image_prompt": ("a tiny baby griffin with a fluffy golden eagle head and small feathered "
                                    "wings on a soft lion-cub body, big amber eyes, tiny beak, palm-sized, adorable fantasy, photorealistic")},
        "scenes": [
            ("a tiny baby griffin in a cozy nest looking up at a soft golden sky, fantasy macro",
             "a tiny griffin gazing up at the sky from its nest, feathers ruffling, slow gentle"),
            ("a tiny baby griffin stretching its little wings wide, warm fantasy macro",
             "a tiny griffin stretching its wings open wide, slow determined cute"),
            ("a tiny baby griffin flapping its wings lifting tiny feet, determined cute, fantasy macro",
             "a tiny griffin flapping its wings, little feet hopping, slow earnest"),
            ("a tiny baby griffin doing a small hop-glide off a low mossy branch, fantasy macro",
             "a tiny griffin hop-gliding off a low branch, wings spread, slow gentle"),
            ("a tiny baby griffin gliding gently through soft golden light, fantasy macro",
             "a tiny griffin gliding through warm golden light, slow graceful"),
            ("a tiny baby griffin landing proudly and fluffing its feathers, fantasy macro",
             "a tiny griffin landing and puffing up proudly, slow happy"),
            ("a tiny baby griffin resting content in its nest at sunset, peaceful fantasy macro",
             "a tiny griffin settling to rest in its nest, sunset glow, very slow peaceful"),
        ],
    },
    # 🦥 baby sloth — SLOWEST COZY MORNING
    "ep16": {
        "title": "Buổi sáng chậm rãi của lười con tí hon", "slug": "tiny_slow_sloth", "kind": "real",
        "music": "output/tiny_animals/_bgm/slow_morning.mp3",
        "entity": {"name": "tiny sloth", "entity_type": "creature",
                   "image_prompt": ("a tiny baby sloth, soft greyish-brown fur, sweet round face with a gentle "
                                    "smile, tiny claws, big calm eyes, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny baby sloth hanging sleepily from a tiny branch in soft morning light, cozy macro",
             "a tiny sloth hanging from a branch blinking very slowly, soft morning light, very slow"),
            ("a tiny baby sloth doing a big slow yawn and stretch, cozy macro",
             "a tiny sloth yawning wide and stretching one arm very slowly, slow gentle"),
            ("a tiny baby sloth slowly reaching for a tiny leaf, cozy macro",
             "a tiny sloth reaching out very slowly for a tiny leaf, slow tender"),
            ("a tiny baby sloth slowly climbing a tiny mossy branch, cozy macro",
             "a tiny sloth climbing a branch in slow motion, one paw at a time, very slow"),
            ("a tiny baby sloth hanging upside down content, cozy macro",
             "a tiny sloth hanging upside down swaying gently, content, very slow"),
            ("a tiny baby sloth being slowly brushed with a soft tiny brush, cozy macro",
             "a soft brush gliding slowly over a tiny sloth's fur, slow soothing"),
            ("a tiny baby sloth asleep hugging a tiny branch, peaceful macro",
             "a tiny sloth sleeping hugging a branch, breathing very slowly, very slow peaceful"),
        ],
    },
    # 🦭 baby seal — BEACH DAY
    "ep17": {
        "title": "Ngày ra biển của hải cẩu con tí hon", "slug": "tiny_beach_seal", "kind": "real",
        "music": "output/tiny_animals/_bgm/beach_day.mp3",
        "entity": {"name": "tiny seal", "entity_type": "creature",
                   "image_prompt": ("a tiny baby seal pup, soft white fluffy fur, big shiny black eyes, tiny "
                                    "whiskers, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny white baby seal pup on warm golden sand beside gentle tiny waves, cozy macro",
             "a tiny seal pup on the sand looking at the little waves, whiskers twitching, slow cozy"),
            ("a tiny baby seal pup wriggling cutely toward the water, sunny beach macro",
             "a tiny seal pup wriggling across the sand toward the sea, slow playful"),
            ("a tiny baby seal pup splashing in shallow clear water, sunny macro",
             "a tiny seal pup splashing in shallow water, soft sparkly ripples, slow playful"),
            ("a tiny baby seal pup nudging a tiny seashell, cozy beach macro",
             "a tiny seal pup nudging a little seashell with its nose, slow curious"),
            ("a tiny baby seal pup lying on warm sand, content in the sun, macro",
             "a tiny seal pup basking on warm sand, eyes half closed, slow content"),
            ("gentle water being poured over a tiny baby seal pup to rinse, cozy macro",
             "soft water trickling over a tiny seal pup, fur glistening, slow gentle"),
            ("a tiny baby seal pup asleep on soft sand under warm light, peaceful macro",
             "a tiny seal pup sleeping on the sand, gentle breathing, very slow peaceful"),
        ],
    },
    # 🦄✨ pegasus foal — STARGAZING NIGHT
    "ep18": {
        "title": "Đêm ngắm sao của tiểu thiên mã tí hon", "slug": "tiny_starlit_pegasus", "kind": "fantasy",
        "music": "output/tiny_animals/_bgm/starlit_meadow.mp3",
        "entity": {"name": "tiny pegasus", "entity_type": "creature",
                   "image_prompt": ("a tiny pegasus foal, soft white coat, small feathered wings, pastel pink "
                                    "and blue mane, big gentle eyes, faint sparkle, palm-sized, adorable fantasy, photorealistic")},
        "scenes": [
            ("a tiny pegasus foal standing in a soft meadow at dusk, warm fading light, fantasy macro",
             "a tiny pegasus foal in a meadow at dusk, mane drifting softly, slow gentle"),
            ("a tiny pegasus foal lifting its head to a starry sky appearing above, fantasy macro",
             "a tiny pegasus lifting its head as stars appear, eyes wide, slow wonder"),
            ("a tiny pegasus foal gently fluttering its little wings under the stars, fantasy macro",
             "a tiny pegasus fluttering its wings softly under starlight, faint sparkles, slow magical"),
            ("a tiny pegasus foal trotting softly through glowing fireflies, fantasy macro",
             "a tiny pegasus trotting gently among drifting fireflies, slow dreamy"),
            ("a tiny pegasus foal surrounded by gentle glowing fireflies in a meadow, fantasy macro",
             "soft glowing fireflies drifting around a calm tiny pegasus, slow magical"),
            ("a tiny pegasus foal lying down in soft grass under the stars, fantasy macro",
             "a tiny pegasus folding down into the grass under the stars, slow tender"),
            ("a tiny pegasus foal asleep, mane faintly glowing under the milky way, peaceful fantasy macro",
             "a tiny pegasus sleeping, mane glowing faintly, stars drifting, very slow peaceful"),
        ],
    },
    # 🦦 baby otter — BATH & FLOAT
    "ep19": {
        "title": "Tắm và thả trôi của rái cá con tí hon", "slug": "tiny_float_otter", "kind": "real",
        "music": "output/tiny_animals/_bgm/otter_float.mp3",
        "entity": {"name": "tiny otter", "entity_type": "creature",
                   "image_prompt": ("a tiny baby otter, sleek soft brown fur, whiskered sweet face, tiny paws, "
                                    "big dark eyes, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny baby otter in cupped hands beside a tiny water basin, cozy warm macro",
             "a tiny otter peeking at the water, whiskers twitching, slow curious cozy"),
            ("a tiny baby otter floating on its back in tiny clear water, cozy macro",
             "a tiny otter floating on its back, paws on its belly, gentle ripples, slow content"),
            ("a tiny baby otter rubbing its little face with its paws, cozy macro",
             "a tiny otter rubbing its face with both paws, slow adorable"),
            ("a tiny baby otter holding a tiny shell snack on its belly, cozy macro",
             "a tiny otter holding a tiny shell on its belly nibbling, slow sweet"),
            ("a tiny baby otter spinning playfully in tiny water, cozy macro",
             "a tiny otter doing a slow playful spin in the water, soft ripples, slow playful"),
            ("a tiny baby otter wrapped in a soft warm towel, cozy macro",
             "a tiny otter snuggled in a warm towel, peeking out, slow cozy"),
            ("a tiny baby otter asleep holding a tiny pebble, peaceful macro",
             "a tiny otter sleeping holding a little pebble, gentle breathing, very slow peaceful"),
        ],
    },
}
