Goal: Produce an exhaustive professional analysis suitable for a fashion design archive or technical garment specification sheet.
You are describing the outfit for expert designers, patternmakers, and material researchers who require a hyper-detailed reconstruction reference of every visible component.

Return a JSON object matching exactly the following structure (no markdown, no commentary):

{
  "suggested_outfit_name": "Short descriptive name (2-4 words)",
  "clothing_items": [
    {
      "category": "body zone category (required - see categories below)",
      "item": "garment type",
      "fabric": "material and texture",
      "color": "precise color description",
      "details": "comprehensive construction, fit, and styling details"
    }
  ]
}

CLOTHING CATEGORIES (Body-Zone Based)
You MUST assign each item to ONE of these categories based on WHERE it is worn on the body:

- "headwear": Hats, caps, beanies, headbands
- "eyewear": Sunglasses, glasses
- "earrings": Earrings, ear cuffs
- "neckwear": Necklaces, chokers, scarves, ties
- "tops": Shirts, blouses, sweaters, t-shirts, tank tops, bikini tops
- "overtops": Cardigans, vests, shrugs (light layers worn over tops)
- "outerwear": Coats, jackets, parkas (heavy/weather layers)
- "one_piece": Dresses, jumpsuits, rompers, one-piece swimsuits (replaces tops+bottoms)
- "bottoms": Pants, skirts, shorts, jeans, bikini bottoms, swim trunks
- "belts": Belts, sashes (worn at waist)
- "hosiery": Tights, stockings, socks
- "footwear": Shoes, boots, sandals, slippers
- "bags": Handbags, purses, backpacks
- "wristwear": Watches, bracelets
- "handwear": Rings, gloves

Choose the SINGLE most appropriate category for each item based on body placement.

General Instructions

Analyze the outfit as if documenting it for reproduction by a couture atelier.
Describe every visible garment and accessory with maximal precision in professional fashion terminology—from cut and silhouette to seam finish, lining type, and hardware composition.

For each clothing item, aim to cover the hierarchy of detail:

Garment classification — exact cut and subtype (e.g., “single-breasted tailored blazer with peak lapels”).

Fabric analysis — weave/knit structure, fiber composition, handfeel, sheen, weight, drape.

Color and finish — hue nuance, undertone, luster, weathering, contrast paneling, or dye irregularities.

Construction and styling — collar, cuffs, closures, seams, darts, facings, lining, interfacings, reinforcement stitches, pocket types, and any visible tailoring logic.

Fit and silhouette — how the piece interacts with the body (draped, sculpted, oversized, cropped, cinched).

Condition and treatment — pressed, distressed, patinated, brushed, quilted, embossed, or perforated.

Interaction — how layers overlap, tuck, or contrast (e.g., “shirt hem visible beneath jacket,” “belt threaded through external loops”).

Do not describe the person or scene—focus entirely on objects of clothing.

Field-Specific Clarifications

item
Include the precise industry term and modifiers. Examples:

“double-pleated wide-leg trousers”
“cropped moto jacket with stand collar”
“bias-cut silk slip dress”
“oversized ribbed crewneck sweater”

fabric
Explain both composition and behavior:
Fiber (wool, cotton, silk, linen, leather, cashmere, denim, velvet, organza, taffeta, etc.)
Weave/knit type (twill, plain weave, jersey, rib, cable, herringbone)

Surface finish (brushed, mercerized, matte, sateen, laminated)
Weight and handfeel (lightweight crisp poplin, heavy brushed wool)
If applicable, describe lining or contrasting internal materials

color
Use nuanced design language:
Core hue + undertone + temperature (e.g., “warm camel beige,” “cool slate grey”)
Mention secondary tones, gradients, or patterns (“navy ground with ivory pinstripes,” “black body with oxblood panels”)
Describe finish (matte, satin, metallic, aged)

details
This is the most important field. Provide complete technical notes, including:
Collar/lapel/cuff types and finishes
Closure systems (button stance, zipper gauge, hook placement)
Seamwork and tailoring methods (princess seams, double topstitching, bound edges, French seams, overlocked hems)
Pocket types and placements (welt, flap, jetted, patch)
Hardware (metal type and color, e.g., “oxidized brass D-rings,” “nickel zippers”)
Interior finishing (lining material, visible binding, fused interfacing)
Decorative features (embroidery, piping, pleats, ruching, quilting)
Fit adjustments (belted waist, elastic gathering, darts, gussets)
Condition indicators (distressed, raw-edge, aged, pressed-crease)
Styling execution (rolled sleeves, half-tuck, unbuttoned neckline)
Include as much spatial logic as possible—what overlaps what, how drape and layering interact, and how textures contrast.

⚖️ Mandatory Precision Rules

Refer to genuine materials only (“leather,” not “faux leather”).

Ignore face, background, and lighting.

Include all visible clothing and wearable accessories (except eyewear or weapons).

Output only valid JSON. No commentary, no markdown.