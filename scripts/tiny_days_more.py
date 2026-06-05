"""More tiny-animal ASMR episodes — each a DISTINCT story arc (not the care-routine) so
videos don't feel repetitive. Mix real + fantasy, different animal per episode, own music.
Merged into EPISODES by tiny_produce. Same schema as tiny_days: title, slug, kind, entity,
music, scenes = (image_prompt_en, motion_prompt_en) × 7. STYLE appended by tiny_produce.
"""

EPISODES_MORE = {
    # ── Arc: RESCUE & HEAL (baby bunny) ──
    "ep5": {
        "title": "Cứu hộ thỏ con tí hon", "slug": "tiny_rescue_bunny", "kind": "real",
        "music": "output/tiny_animals/_bgm/rescue_warmth.mp3",
        "entity": {"name": "tiny bunny", "entity_type": "creature",
                   "image_prompt": ("a tiny fluffy grey-white baby bunny, big dark round eyes, "
                                    "small twitching pink nose, soft long ears, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny shivering wet baby bunny found under a leaf in the rain, cupped in gentle hands, soft sad cozy macro",
             "a tiny wet bunny shivering gently in cupped hands, rain blurred behind, slow tender"),
            ("a tiny bunny being wrapped in a small warm towel beside a soft fireplace glow, cozy macro",
             "gentle hands wrapping a tiny bunny in a warm towel, firelight flickering soft, slow cozy"),
            ("a tiny bunny being gently dried with warm air, fur fluffing up softly, warm cozy macro",
             "a tiny bunny's fur fluffing softly in warm air, ears perking a little, slow gentle"),
            ("a tiny bunny sipping warm milk from a tiny dropper bottle, warm cozy macro",
             "a tiny bunny drinking warm milk from a tiny bottle, nose twitching, slow tender cozy"),
            ("a tiny bunny resting in a soft knitted blanket nest, looking brighter, warm cozy macro",
             "a tiny bunny nestling into a soft blanket, eyes brightening, breathing calm, slow cozy"),
            ("a tiny bunny nibbling a small carrot, lively and healed, warm cozy macro",
             "a tiny recovered bunny nibbling a tiny carrot happily, ears up, gentle playful slow"),
            ("a tiny bunny snuggled content and warm in a cozy blanket, peaceful macro",
             "a tiny bunny curled content in a warm blanket, slow happy breathing, very slow peaceful"),
        ],
    },
    # ── Arc: SPA DAY (pomeranian puppy) ──
    "ep6": {
        "title": "Spa thư giãn cún tí hon", "slug": "tiny_spa_puppy", "kind": "real",
        "music": "output/tiny_animals/_bgm/spa_serene.mp3",
        "entity": {"name": "tiny puppy", "entity_type": "creature",
                   "image_prompt": ("a tiny fluffy orange pomeranian puppy, round black eyes, "
                                    "tiny black nose, super fluffy fur, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny pomeranian puppy in a tiny white robe with a small towel on its head, cozy spa macro",
             "a tiny puppy in a robe blinking slowly, steam drifting softly, slow serene cozy"),
            ("a tiny puppy in a tiny bubble bath with soft white foam, warm spa macro",
             "a tiny puppy sitting in soft foam, bubbles gently rising and popping, slow calm"),
            ("a tiny puppy getting a gentle fingertip back massage, relaxed spa macro",
             "gentle fingertips massaging a tiny puppy's back, puppy melting relaxed, slow soothing"),
            ("a tiny puppy being gently brushed, fluffy fur smoothed, warm spa macro",
             "a soft brush gliding through a tiny puppy's fur, slow gentle relaxing"),
            ("a tiny puppy with two cucumber slices nearby and a tiny face mask, spa macro",
             "a tiny puppy lying back with cucumber slices, very still relaxed, slow serene"),
            ("a tiny puppy soaking paws in a warm tiny bowl, blissful spa macro",
             "a tiny puppy soaking its paws, eyes half closed blissful, gentle steam, slow calm"),
            ("a tiny puppy lying back fully relaxed eyes closed, soft towel, peaceful spa macro",
             "a tiny puppy fully relaxed breathing slowly, blissful, very slow peaceful"),
        ],
    },
    # ── Arc: BEDTIME / SLEEP (baby unicorn) ──
    "ep7": {
        "title": "Đêm ngủ ngon kỳ lân con", "slug": "tiny_bedtime_unicorn", "kind": "fantasy",
        "music": "output/tiny_animals/_bgm/lullaby_night.mp3",
        "entity": {"name": "tiny unicorn", "entity_type": "creature",
                   "image_prompt": ("a palm-sized baby unicorn with soft white coat, pastel pink "
                                    "and lilac mane, tiny golden spiral horn, big gentle eyes, adorable, fantasy, photorealistic")},
        "scenes": [
            ("a tiny baby unicorn in a cozy miniature bedroom at dusk, warm lamp glow, fantasy macro",
             "a tiny unicorn yawning softly in a cozy room, warm lamp flicker, slow sleepy"),
            ("a tiny unicorn in a small warm bath with faint sparkle, cozy fantasy macro",
             "a tiny unicorn in a warm bath, faint sparkles drifting, slow calm magical"),
            ("a tiny unicorn sipping warm milk from a tiny cup, sleepy cozy fantasy macro",
             "a tiny unicorn sipping warm milk, eyes drooping sleepy, slow tender"),
            ("a tiny unicorn beside a tiny open storybook, listening sleepily, warm fantasy macro",
             "a tiny unicorn nodding off beside an open storybook, pages soft, slow sleepy"),
            ("a tiny star-shaped nightlight glowing softly beside a tiny unicorn, fantasy macro",
             "a tiny star nightlight glowing on, soft warm light spreading, slow calm"),
            ("a tiny unicorn being tucked under a tiny blanket with a plush toy, cozy fantasy macro",
             "a tiny blanket settling over a tiny unicorn hugging a plush, slow tender peaceful"),
            ("a tiny unicorn asleep, mane softly glowing under tiny floating stars, peaceful fantasy macro",
             "a tiny unicorn sleeping, mane glowing faintly, tiny stars drifting, very slow peaceful"),
        ],
    },
    # ── Arc: RAINY DAY COZY (baby fox) ──
    "ep8": {
        "title": "Ngày mưa ấm cúng cáo con", "slug": "tiny_rainy_fox", "kind": "real",
        "music": "output/tiny_animals/_bgm/rainy_window.mp3",
        "entity": {"name": "tiny fox", "entity_type": "creature",
                   "image_prompt": ("a tiny baby red fox, soft orange fur with white cheeks and chest, "
                                    "big amber eyes, small black nose, fluffy tail, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny baby fox watching raindrops run down a window, cozy warm room, macro",
             "a tiny fox watching rain trails on the glass, ears soft, slow calm cozy"),
            ("a tiny fox burrowing into a soft folded blanket by the window, cozy macro",
             "a tiny fox snuggling deep into a soft blanket, slow cozy gentle"),
            ("a tiny fox beside a tiny cup of warm tea with rising steam, rainy window, cozy macro",
             "steam rising from a tiny tea cup beside a calm fox, rain behind, slow mellow"),
            ("a tiny fox with ears twitching toward the rain, peaceful, cozy macro",
             "a tiny fox's ears twitching to soft rain, eyes calm, slow soothing"),
            ("a tiny fox resting its head on a tiny open book, droopy eyes, cozy macro",
             "a tiny fox resting on a book, eyelids drooping, rain soft behind, slow sleepy"),
            ("a tiny fox curling into a cozy ball with its fluffy tail, warm macro",
             "a tiny fox curling up wrapping its tail around itself, slow cozy"),
            ("a tiny fox asleep by the rainy window under a soft lamp, peaceful macro",
             "a tiny fox sleeping by the window, rain blurred, lamp glow soft, very slow peaceful"),
        ],
    },
    # ── Arc: TINY KITCHEN / BAKING (tiny mouse) ──
    "ep9": {
        "title": "Bếp tí hon chuột nhắt làm bánh", "slug": "tiny_kitchen_mouse", "kind": "real",
        "music": "output/tiny_animals/_bgm/kitchen_bake.mp3",
        "entity": {"name": "tiny mouse", "entity_type": "creature",
                   "image_prompt": ("a tiny brown mouse wearing a tiny apron, round black eyes, "
                                    "big soft ears, tiny pink paws, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny mouse in a tiny apron at a miniature wooden kitchen counter, warm cozy macro",
             "a tiny mouse looking proudly at a tiny counter, warm kitchen light, slow cozy"),
            ("a tiny mouse kneading a small ball of dough with its paws, warm cozy macro",
             "a tiny mouse pressing and kneading tiny dough, paws working gently, slow cozy"),
            ("tiny cookies on a tiny tray going into a tiny warm oven, golden glow, cozy macro",
             "a tiny tray of cookies sliding into a warm glowing oven, slow cozy"),
            ("a tiny mouse pouring tiny tea into a thimble cup, steam rising, warm cozy macro",
             "a tiny mouse pouring tea into a thimble, steam curling up, slow gentle"),
            ("a tiny mouse setting a tiny table with warm cookies, cozy macro",
             "a tiny mouse arranging tiny cookies on a little table, slow careful cozy"),
            ("a tiny mouse nibbling a warm cookie with delight, cozy macro",
             "a tiny mouse taking a happy bite of a warm cookie, cheeks puffing, slow joyful"),
            ("a tiny mouse content with a full belly resting by the warm oven, peaceful macro",
             "a tiny mouse patting its full belly resting by the oven glow, very slow peaceful"),
        ],
    },
    # ── Arc: BUILD A HOME / NEST (baby phoenix) ──
    "ep10": {
        "title": "Làm tổ ấm phượng hoàng con", "slug": "tiny_build_phoenix", "kind": "fantasy",
        "music": "output/tiny_animals/_bgm/nest_build.mp3",
        "entity": {"name": "tiny phoenix", "entity_type": "creature",
                   "image_prompt": ("a palm-sized baby phoenix with soft orange-gold feathers, "
                                    "warm ember glow, tiny crest, big warm eyes, adorable, fantasy, photorealistic")},
        "scenes": [
            ("a tiny baby phoenix choosing a cozy nook with soft twigs nearby, warm fantasy macro",
             "a tiny phoenix looking around a cozy nook, feathers glowing faint, slow gentle"),
            ("a tiny phoenix arranging soft twigs into a nest base, warm fantasy macro",
             "a tiny phoenix nudging twigs into a circle, careful gentle, slow cozy"),
            ("a tiny phoenix building up the nest walls with soft moss, warm fantasy macro",
             "a tiny phoenix tucking moss into nest walls, slow careful cozy"),
            ("a tiny phoenix lining the nest with soft golden feathers, warm fantasy macro",
             "a tiny phoenix smoothing golden feathers into the nest, slow gentle glowing"),
            ("a tiny phoenix adding tiny glowing embers like treasures to the nest, fantasy macro",
             "a tiny phoenix placing glowing embers in the nest, warm light pulsing, slow magical"),
            ("a tiny phoenix settling happily into its finished glowing nest, fantasy macro",
             "a tiny phoenix snuggling into the warm finished nest, feathers settling, slow content"),
            ("a tiny phoenix curled asleep in its warm glowing nest, peaceful fantasy macro",
             "a tiny phoenix sleeping in its glowing nest, ember light breathing softly, very slow peaceful"),
        ],
    },
    # ── Arc: TWO FRIENDS (hedgehog + chick) ──
    "ep11": {
        "title": "Đôi bạn tí hon nhím và gà con", "slug": "tiny_friends_duo", "kind": "real",
        "music": "output/tiny_animals/_bgm/friends_play.mp3",
        "entity": {"name": "tiny hedgehog and chick", "entity_type": "creature",
                   "image_prompt": ("a tiny round baby hedgehog with soft brown spines and a sweet face "
                                    "next to a tiny fluffy yellow chick with a small orange beak, both palm-sized, "
                                    "adorable best friends, photorealistic")},
        "scenes": [
            ("a tiny hedgehog and a tiny yellow chick meeting nose-to-beak, curious and sweet, cozy macro",
             "a tiny hedgehog and chick leaning in nose-to-beak, blinking, slow gentle cute"),
            ("a tiny hedgehog and chick sharing a single tiny berry between them, cozy macro",
             "a tiny hedgehog and chick nibbling the same berry from each side, slow sweet"),
            ("a tiny hedgehog and chick chasing a tiny acorn together, playful cozy macro",
             "a tiny hedgehog and chick nudging a tiny acorn back and forth, gentle playful slow"),
            ("a tiny hedgehog and chick splashing gently in a tiny water dish, cozy macro",
             "a tiny hedgehog and chick dipping into a tiny water dish, soft splashes, slow playful"),
            ("a tiny chick turned away briefly while the hedgehog gently nudges it, sweet cozy macro",
             "a tiny hedgehog softly nudging a turned-away chick, tender, slow gentle"),
            ("a tiny hedgehog and chick nuzzling, friends again, warm cozy macro",
             "a tiny hedgehog and chick nuzzling close together, slow tender happy"),
            ("a tiny hedgehog and chick napping snuggled together, peaceful cozy macro",
             "a tiny hedgehog and chick sleeping snuggled side by side, gently breathing, very slow peaceful"),
        ],
    },
    # ── Arc: FESTIVAL / BIRTHDAY (baby panda) ──
    "ep12": {
        "title": "Sinh nhật tí hon gấu trúc con", "slug": "tiny_party_panda", "kind": "real",
        "music": "output/tiny_animals/_bgm/festival_party.mp3",
        "entity": {"name": "tiny panda", "entity_type": "creature",
                   "image_prompt": ("a tiny fluffy baby panda, classic black and white fur, big black "
                                    "eye patches, round dark eyes, tiny round ears, palm-sized, adorable, photorealistic")},
        "scenes": [
            ("a tiny baby panda hanging a tiny paper garland for a party, warm cozy macro",
             "a tiny panda reaching up to hang a tiny garland, party setup, slow happy cozy"),
            ("a tiny birthday cake with a single candle in front of a tiny panda, warm cozy macro",
             "a tiny panda gazing at a tiny cake with a candle, eyes wide, slow joyful"),
            ("a tiny candle being lit, warm glow on a tiny panda's face, cozy macro",
             "a tiny candle flame flickering to life, warm glow on the panda, slow cozy"),
            ("a tiny panda closing its eyes to make a wish, sweet cozy macro",
             "a tiny panda closing its eyes wishing, tiny paws together, slow tender"),
            ("a tiny panda opening a tiny wrapped gift box, excited cozy macro",
             "a tiny panda pulling the ribbon off a tiny gift, slow happy gentle"),
            ("gentle paper confetti drifting around a delighted tiny panda, cozy macro",
             "soft paper confetti drifting down around a happy tiny panda, slow joyful"),
            ("a tiny panda hugging its new gift, content under soft party lights, peaceful macro",
             "a tiny panda hugging its gift close, party lights glowing soft, very slow content"),
        ],
    },
}
