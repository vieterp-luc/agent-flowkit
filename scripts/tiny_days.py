"""Content data for the 'Chăm sóc động vật tí hon' (tiny-animal care) ASMR series.
Mix of REAL cute animals + FANTASY tiny creatures. Cozy "care routine" arc, NO narration
(music-backed). Each episode = title, slug, scenes = (image_prompt_en, motion_prompt_en).
Consumed by scripts/tiny_produce.py. Motion = gentle camera + soft animal movement.
"""

STYLE = ("adorable, cozy, macro miniature, soft warm lighting, shallow depth of field, "
         "photorealistic, vertical 9:16, no text, wholesome")

# Cozy care-routine arc per episode: reveal → feed → bathe → play → habitat → cuddle → sleep
EPISODES = {
    "ep1": {
        "title": "Chăm sóc hamster tí hon",
        "slug": "tiny_hamster",
        "kind": "real",
        "music": "output/tiny_animals/_bgm/cozy_playful.mp3",
        "entity": {
            "name": "tiny hamster",
            "entity_type": "creature",
            "image_prompt": ("a tiny golden-brown Syrian hamster, round black shiny eyes, "
                             "soft cream-colored belly, tiny pink nose, small rounded ears, "
                             "fluffy plush fur, palm-sized, adorable, photorealistic"),
        },
        "scenes": [
            ("an adorable tiny hamster sitting in a person's cupped palm, soft warm light, cozy macro",
             "a tiny hamster in cupped hands gently sniffing and twitching its nose, slow soft cozy"),
            ("a tiny hamster nibbling a miniature sunflower seed from a tiny wooden bowl, warm cozy macro",
             "a tiny hamster nibbling a small seed from a tiny bowl, paws moving gently, slow cozy"),
            ("a tiny hamster being gently groomed with a small soft brush, warm cozy macro",
             "a tiny soft brush gently grooming a hamster's fur, slow gentle, cozy warm"),
            ("a tiny hamster playing in a miniature wooden playground with tiny ladders, cozy macro",
             "a tiny hamster climbing a miniature wooden ladder, gentle playful movement, slow cozy"),
            ("a cozy miniature hamster house with tiny furniture and soft bedding, warm macro detail",
             "slow gentle pan across a cozy miniature hamster house with tiny furniture, warm soft light"),
            ("a tiny hamster snuggling into a person's gentle fingertips, affectionate warm cozy macro",
             "a tiny hamster nuzzling softly into gentle fingertips, slow tender cozy"),
            ("a tiny hamster curled up asleep in a tiny knitted bed, soft warm light, peaceful macro",
             "a tiny hamster sleeping curled in a tiny knitted bed, gently breathing, very slow peaceful"),
        ],
    },
    "ep2": {
        "title": "Chăm sóc rồng con tí hon",
        "slug": "tiny_baby_dragon",
        "kind": "fantasy",
        "music": "output/tiny_animals/_bgm/dragon_glow.mp3",
        "entity": {
            "name": "tiny baby dragon",
            "entity_type": "creature",
            "image_prompt": ("a palm-sized baby dragon with emerald-green scales, soft golden "
                             "underbelly, small translucent amber wings, big friendly amber eyes, "
                             "tiny rounded horns, gentle smile, cute, fantasy, photorealistic"),
        },
        "scenes": [
            ("an adorable palm-sized baby dragon sitting in cupped hands, softly glowing scales, cozy fantasy macro",
             "a tiny baby dragon in cupped hands blinking and flicking its little wings, slow magical cozy"),
            ("a tiny baby dragon eating a glowing miniature berry from a tiny bowl, fantasy cozy macro",
             "a tiny baby dragon nibbling a glowing berry from a tiny bowl, gentle, slow magical cozy"),
            ("a tiny baby dragon being gently bathed in a tiny bowl of water with soft bubbles, fantasy cozy",
             "a tiny baby dragon splashing gently in a tiny water bowl, soft bubbles, slow cozy magical"),
            ("a tiny baby dragon playing with a small glowing ball, fantasy cozy warm macro",
             "a tiny baby dragon chasing a small glowing ball, playful gentle hops, slow cozy"),
            ("a cozy miniature dragon nest with tiny glowing treasures and warm glow, fantasy macro detail",
             "slow gentle pan across a cozy miniature dragon nest with tiny glowing treasures, warm"),
            ("a tiny baby dragon nuzzling into a person's gentle fingertips, affectionate fantasy macro",
             "a tiny baby dragon nuzzling softly into fingertips, wings folding, slow tender cozy"),
            ("a tiny baby dragon curled asleep on a soft cushion with a faint warm glow, peaceful fantasy macro",
             "a tiny baby dragon sleeping curled on a cushion, faint glow pulsing softly, very slow peaceful"),
        ],
    },
    "ep3": {
        "title": "Chăm sóc mèo con tí hon",
        "slug": "tiny_kitten",
        "kind": "real",
        "music": "output/tiny_animals/_bgm/kitten_play.mp3",
        "entity": {
            "name": "tiny kitten",
            "entity_type": "creature",
            "image_prompt": ("a tiny grey tabby kitten with white paws and white chest, big round "
                             "blue eyes, small pink nose, soft fluffy fur, palm-sized, adorable, "
                             "photorealistic"),
        },
        "scenes": [
            ("an adorable tiny kitten sitting in a person's cupped palm, soft warm light, cozy macro",
             "a tiny kitten in cupped hands blinking slowly and tilting its head, slow soft cozy"),
            ("a tiny kitten lapping milk from a miniature saucer, warm cozy macro",
             "a tiny kitten gently lapping milk from a tiny saucer, slow cozy warm"),
            ("a tiny kitten being gently dried with a soft tiny towel after a bath, warm cozy macro",
             "a soft tiny towel gently drying a kitten, slow gentle, cozy warm"),
            ("a tiny kitten batting a tiny ball of yarn, playful cozy macro",
             "a tiny kitten softly batting a tiny ball of yarn, gentle playful, slow cozy"),
            ("a cozy miniature kitten bedroom with tiny furniture and a tiny basket, warm macro detail",
             "slow gentle pan across a cozy miniature kitten room with tiny furniture, warm soft light"),
            ("a tiny kitten nuzzling into a person's gentle fingertips, affectionate warm cozy macro",
             "a tiny kitten nuzzling softly into gentle fingertips, slow tender cozy"),
            ("a tiny kitten curled up asleep in a tiny basket with a soft blanket, peaceful warm macro",
             "a tiny kitten sleeping curled in a tiny basket, gently breathing, very slow peaceful"),
        ],
    },
    "ep4": {
        "title": "Chăm sóc voi tí hon lòng bàn tay",
        "slug": "tiny_mini_elephant",
        "kind": "fantasy",
        "music": "output/tiny_animals/_bgm/elephant_calm.mp3",
        "entity": {
            "name": "tiny elephant",
            "entity_type": "creature",
            "image_prompt": ("a palm-sized baby elephant with soft grey wrinkled skin, big floppy "
                             "ears, short curled trunk, gentle dark eyes, tiny white tusks, "
                             "adorable, photorealistic"),
        },
        "scenes": [
            ("an adorable palm-sized tiny elephant standing in cupped hands, soft warm light, cozy fantasy macro",
             "a tiny elephant in cupped hands gently swaying its little trunk and ears, slow soft cozy"),
            ("a tiny elephant drinking water with its trunk from a miniature bowl, cozy fantasy macro",
             "a tiny elephant sipping water with its trunk from a tiny bowl, gentle, slow cozy"),
            ("a tiny elephant being gently washed with a small sponge and soft bubbles, cozy fantasy macro",
             "a small sponge gently washing a tiny elephant, soft bubbles, slow cozy warm"),
            ("a tiny elephant playing with a small soft ball in a cozy miniature garden, fantasy macro",
             "a tiny elephant nudging a small soft ball with its trunk, gentle playful, slow cozy"),
            ("a cozy miniature elephant home with tiny hay and soft bedding in a warm garden, macro detail",
             "slow gentle pan across a cozy miniature elephant home with tiny hay, warm soft light"),
            ("a tiny elephant nuzzling its trunk into a person's gentle fingertips, affectionate fantasy macro",
             "a tiny elephant curling its trunk softly around a fingertip, slow tender cozy"),
            ("a tiny elephant lying asleep on a soft cushion under a tiny blanket, peaceful fantasy macro",
             "a tiny elephant sleeping on a soft cushion, ears gently settling, very slow peaceful"),
        ],
    },
}
