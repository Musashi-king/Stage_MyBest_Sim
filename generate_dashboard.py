import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "donnees-test-mybestsim"
OUTPUT = ROOT / "dashboard.html"
INDEX_OUTPUT = ROOT / "index.html"
REQUIRED_COLUMNS = {
    "sku",
    "provider",
    "product_name",
    "country_name",
    "data_gb",
    "data_display",
    "validity_days",
    "price",
    "currency",
    "network",
}


def read_csv(path):
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise UnicodeError(f"Impossible de décoder {path.name}")

    records = csv.DictReader(text.splitlines())
    missing = REQUIRED_COLUMNS.difference(records.fieldnames or [])
    if missing:
        raise ValueError(f"{path.name}: colonnes manquantes: {', '.join(sorted(missing))}")

    products = []
    for line_number, row in enumerate(records, start=2):
        try:
            price = float(row["price"].replace(",", "."))
            data = float(row["data_gb"].replace(",", ".")) if row["data_gb"].strip() else None
            validity = int(row["validity_days"]) if row["validity_days"].strip() else None
        except ValueError as error:
            raise ValueError(f"{path.name}:{line_number}: prix, data ou validité invalide") from error

        products.append(
            {
                "sku": row["sku"],
                "provider": row["provider"],
                "name": row["product_name"],
                "destination": row["country_name"],
                "data": data,
                "dataLabel": row["data_display"],
                "validity": validity,
                "price": price,
                "currency": row["currency"],
                "network": row["network"],
            }
        )
    return products


def build_dashboard(products):
    payload = json.dumps(products, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = r"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Tableau de bord interactif du catalogue eSIM MyBestSim : prix, data et répartition par fournisseur.">
  <title>Catalogue eSIM — MyBestSim</title>
  <style>
    :root{color-scheme:light;--ink:#142b35;--muted:#62747a;--line:#e4ece9;--paper:#f5f8f6;--green:#087e70;--mint:#d9f3eb;--orange:#ffbd77}
    *{box-sizing:border-box}
    body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
    header{padding:30px max(24px,calc((100% - 1180px)/2));background:#102c36;color:white}
    .eyebrow{margin:0 0 5px;color:#9bdccb;font-size:12px;font-weight:750;letter-spacing:.12em;text-transform:uppercase}
    h1{margin:0;font-size:clamp(25px,4vw,38px);letter-spacing:-.035em}
    header p:last-child{margin:8px 0 0;color:#c6d7d8}
    main{max-width:1180px;margin:28px auto;padding:0 20px 48px}
    .cards{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}
    .card,.panel{background:white;border:1px solid var(--line);border-radius:14px;box-shadow:0 3px 12px #173a3510}
    .card{min-height:125px;padding:18px}
    .label{color:var(--muted);font-size:13px;font-weight:650}
    .value{display:block;margin:11px 0 1px;font-size:clamp(22px,2.5vw,30px);font-weight:780;letter-spacing:-.04em;line-height:1.1}
    .sub{color:var(--muted);font-size:12px}
    .layout{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(290px,.8fr);gap:16px;margin-top:18px}
    .panel{padding:21px}
    h2{margin:0;font-size:18px;letter-spacing:-.02em}
    .panel-note{margin:4px 0 15px;color:var(--muted);font-size:12px}
    .bar-list{display:grid;gap:9px}
    .bar-row{display:grid;grid-template-columns:minmax(88px,125px) 1fr 45px;align-items:center;gap:9px}
    .bar-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px}
    .bar-track{height:10px;border-radius:10px;background:#edf3f0;overflow:hidden}
    .bar-fill{height:100%;border-radius:10px;background:var(--green)}
    .bar-count{text-align:right;font-size:12px;font-weight:700}
    .distribution-layout{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:18px}
    .distribution-list{display:grid;gap:11px}
    .distribution-row{display:grid;grid-template-columns:minmax(58px,82px) 1fr 74px;align-items:center;gap:9px}
    .distribution-name,.distribution-count{font-size:12px}
    .distribution-count{text-align:right;font-weight:700}
    .distribution-track{height:9px;border-radius:10px;background:#edf3f0;overflow:hidden}
    .distribution-fill{height:100%;border-radius:10px;background:var(--green)}
    .network-fill{background:#49a990}
    .metric-pair{display:grid;grid-template-columns:1fr 1fr;gap:9px}
    .metric-tile{padding:13px;border-radius:10px;background:#f2f8f5}
    .metric-tile strong{display:block;font-size:21px;letter-spacing:-.03em}
    .metric-tile span{color:var(--muted);font-size:12px}
    .chart-note{margin:13px 0 0;color:var(--muted);font-size:11px}
    .insights{display:grid;gap:10px}
    .insight{padding:12px 13px;border-radius:10px;background:#f2f8f5}
    .insight strong{display:block;margin-bottom:2px}
    .insight span{color:var(--muted);font-size:13px}
    .method{margin-top:15px;padding:13px 14px;border-left:3px solid var(--orange);border-radius:5px;background:#fff8ef;color:#57452f;font-size:12px}
    .table-panel{margin-top:18px;padding:0;overflow:hidden}
    .table-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:18px 20px;border-bottom:1px solid var(--line)}
    .controls{display:flex;gap:8px;flex-wrap:wrap}
    input,select{min-height:38px;padding:7px 10px;border:1px solid #d5e0dc;border-radius:8px;background:white;color:var(--ink);font:inherit;font-size:13px}
    input{width:min(250px,45vw)}
    .scroll{overflow-x:auto}
    table{width:100%;border-collapse:collapse;white-space:nowrap}
    th,td{padding:11px 14px;border-bottom:1px solid #edf1ef;text-align:left;font-size:13px}
    th{background:#fbfcfb;color:var(--muted);font-size:11px;letter-spacing:.04em;text-transform:uppercase}
    td:nth-child(2){max-width:360px;overflow:hidden;text-overflow:ellipsis}
    td:last-child{text-align:right;font-weight:750}
    .pagination{display:flex;align-items:center;justify-content:space-between;padding:13px 18px;color:var(--muted);font-size:12px}
    button{padding:7px 12px;border:1px solid #d5e0dc;border-radius:7px;background:white;color:var(--ink);font:inherit;cursor:pointer}
    button:disabled{opacity:.4;cursor:default}
    footer{margin-top:16px;color:var(--muted);font-size:11px;text-align:right}
    @media(max-width:900px){.cards{grid-template-columns:repeat(3,minmax(0,1fr))}.layout{grid-template-columns:1fr}.distribution-layout{grid-template-columns:repeat(2,minmax(0,1fr))}}
    @media(max-width:560px){header{padding:23px 20px}.cards{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}main{padding:0 12px 32px;margin-top:16px}.card{min-height:110px;padding:14px}.panel{padding:16px}.table-head{align-items:flex-start;flex-direction:column}.controls{width:100%}input{width:100%;flex:1}.distribution-layout{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">MyBestSim · Data catalogue</p>
    <h1>Le catalogue eSIM, en un coup d’œil</h1>
    <p id="subtitle">Analyse des fichiers fournisseurs</p>
  </header>
  <main>
    <section class="cards" aria-label="Indicateurs clés">
      <article class="card"><span class="label">Cartes eSIM</span><strong class="value" id="total">—</strong><span class="sub">produits au catalogue</span></article>
      <article class="card"><span class="label">Prix supérieur à 100 €</span><strong class="value" id="over100">—</strong><span class="sub" id="over100share"></span></article>
      <article class="card"><span class="label">Fourchette de prix</span><strong class="value" id="range">—</strong><span class="sub">prix min. → prix max.</span></article>
      <article class="card"><span class="label">Data moyenne</span><strong class="value" id="avgdata">—</strong><span class="sub" id="dataCoverage"></span></article>
      <article class="card"><span class="label">Prix moyen</span><strong class="value" id="avgprice">—</strong><span class="sub">toutes les offres, en EUR</span></article>
    </section>
    <section class="layout">
      <article class="panel">
        <h2>Offres par fournisseur</h2>
        <p class="panel-note">Nombre de références présentes dans les fichiers importés</p>
        <div class="bar-list" id="providers"></div>
      </article>
      <article class="panel">
        <h2>À retenir</h2>
        <p class="panel-note">Quelques repères complémentaires sur le catalogue</p>
        <div class="insights" id="insights"></div>
        <div class="method"><strong>Note de calcul.</strong> Les offres « illimitées » ne donnent pas de volume numérique : elles sont exclues de la moyenne de data, mais incluses dans les autres indicateurs. Les montants sont en euros, tels que fournis par les CSV.</div>
      </article>
    </section>
    <section class="distribution-layout" aria-label="Répartition des offres">
      <article class="panel">
        <h2>Volumes de data</h2>
        <p class="panel-note">Répartition des forfaits avec volume chiffré</p>
        <div class="distribution-list" id="dataDistribution"></div>
      </article>
      <article class="panel">
        <h2>Durée de validité</h2>
        <p class="panel-note">Nombre de jours inclus dans les offres</p>
        <div class="distribution-list" id="validityDistribution"></div>
      </article>
      <article class="panel">
        <h2>Réseau &amp; prix par Go</h2>
        <p class="panel-note">Réseaux annoncés dans les fichiers fournisseurs</p>
        <div class="distribution-list" id="networkDistribution"></div>
        <div class="metric-pair" id="valueMetrics" style="margin-top:18px"></div>
        <p class="chart-note">Prix par Go calculé uniquement pour les offres à volume chiffré. Les destinations et durées variant, cet indicateur est un repère global, pas une comparaison à caractéristiques égales.</p>
      </article>
    </section>
    <section class="panel table-panel">
      <div class="table-head">
        <div><h2>Explorer les offres</h2><div class="panel-note" style="margin-bottom:0">Recherche sur le produit et la destination</div></div>
        <div class="controls"><input id="search" type="search" placeholder="Ex. Japon, 10 Go…" aria-label="Rechercher une offre"><select id="providerFilter" aria-label="Filtrer par fournisseur"><option value="">Tous les fournisseurs</option></select></div>
      </div>
      <div class="scroll"><table>
        <thead><tr><th>Fournisseur</th><th>Produit</th><th>Destination</th><th>Data</th><th>Validité</th><th>Réseau</th><th>Prix</th></tr></thead>
        <tbody id="productRows"></tbody>
      </table></div>
      <div class="pagination"><span id="pageLabel"></span><div><button id="previous">Précédent</button> <button id="next">Suivant</button></div></div>
    </section>
    <footer id="source"></footer>
  </main>
  <script id="catalogue" type="application/json">__DATA__</script>
  <script>
    const rows = JSON.parse(document.getElementById("catalogue").textContent);
    const money = value => new Intl.NumberFormat("fr-FR", {style:"currency",currency:"EUR",maximumFractionDigits:2}).format(value);
    const number = value => new Intl.NumberFormat("fr-FR",{maximumFractionDigits:2}).format(value);
    const providers = [...new Set(rows.map(row=>row.provider))].sort((a,b)=>a.localeCompare(b,"fr"));
    const prices = rows.map(row=>row.price).filter(Number.isFinite);
    const numericData = rows.filter(row=>Number.isFinite(row.data));
    const unlimited = rows.filter(row=>row.data === null);
    const total = rows.length;
    document.getElementById("total").textContent = number(total);
    document.getElementById("subtitle").textContent = `${number(total)} produits · ${providers.length} fournisseurs · données issues des fichiers CSV`;
    const expensive = prices.filter(price=>price>100).length;
    document.getElementById("over100").textContent = number(expensive);
    document.getElementById("over100share").textContent = `${number(expensive/total*100)} % du catalogue`;
    document.getElementById("range").textContent = `${money(Math.min(...prices))} – ${money(Math.max(...prices))}`;
    document.getElementById("avgprice").textContent = money(prices.reduce((sum,value)=>sum+value,0)/prices.length);
    document.getElementById("avgdata").textContent = `${number(numericData.reduce((sum,row)=>sum+row.data,0)/numericData.length)} Go`;
    document.getElementById("dataCoverage").textContent = `sur ${number(numericData.length)} offres avec volume chiffré`;
    const median = values => {
      const sorted = [...values].sort((a,b)=>a-b);
      const middle = Math.floor(sorted.length/2);
      return sorted.length % 2 ? sorted[middle] : (sorted[middle-1]+sorted[middle])/2;
    };
    const distributionMarkup = (items, totalCount, formatter, fillClass="") => {
      const maxCount = Math.max(...items.map(item=>item.count));
      return items.map(item=>`<div class="distribution-row"><span class="distribution-name">${escapeHtml(formatter(item.value))}</span><div class="distribution-track"><div class="distribution-fill ${fillClass}" style="width:${item.count/maxCount*100}%" title="${number(item.count)} offres"></div></div><span class="distribution-count">${number(item.count)} · ${number(item.count/totalCount*100)} %</span></div>`).join("");
    };
    const countValues = values => {
      const counts = new Map();
      values.forEach(value=>counts.set(value,(counts.get(value)||0)+1));
      return [...counts.entries()].map(([value,count])=>({value,count})).sort((a,b)=>Number(a.value)-Number(b.value));
    };
    const dataDistribution = countValues(numericData.map(row=>row.data));
    const validityDistribution = countValues(rows.filter(row=>row.validity!==null).map(row=>row.validity));
    const networkDistribution = countValues(rows.map(row=>row.network).filter(Boolean));
    document.getElementById("dataDistribution").innerHTML = distributionMarkup(dataDistribution,numericData.length,value=>`${number(value)} Go`);
    document.getElementById("validityDistribution").innerHTML = distributionMarkup(validityDistribution,rows.length,value=>`${number(value)} jours`);
    document.getElementById("networkDistribution").innerHTML = distributionMarkup(networkDistribution,rows.length,value=>value,"network-fill");
    const pricePerGb = numericData.filter(row=>row.data>0).map(row=>row.price/row.data);
    const medianData = median(numericData.map(row=>row.data));
    document.getElementById("valueMetrics").innerHTML = [
      `<div class="metric-tile"><strong>${money(median(pricePerGb))}</strong><span>prix médian par Go</span></div>`,
      `<div class="metric-tile"><strong>${number(medianData)} Go</strong><span>volume médian</span></div>`
    ].join("");
    const counts = providers.map(provider=>({provider,count:rows.filter(row=>row.provider===provider).length})).sort((a,b)=>b.count-a.count||a.provider.localeCompare(b.provider,"fr"));
    const maxCount = Math.max(...counts.map(item=>item.count));
    document.getElementById("providers").innerHTML = counts.map(item=>`<div class="bar-row"><span class="bar-name" title="${escapeHtml(item.provider)}">${escapeHtml(item.provider)}</span><div class="bar-track"><div class="bar-fill" style="width:${item.count/maxCount*100}%"></div></div><span class="bar-count">${number(item.count)}</span></div>`).join("");
    const destinationCounts = new Map();
    rows.forEach(row=>destinationCounts.set(row.destination,(destinationCounts.get(row.destination)||0)+1));
    const topDestination = [...destinationCounts.entries()].sort((a,b)=>b[1]-a[1])[0];
    const unlimitedShare = unlimited.length/total*100;
    document.getElementById("insights").innerHTML = [
      `<div class="insight"><strong>${number(providers.length)} fournisseurs</strong><span>La plus grande offre compte ${number(counts[0].count)} références (${escapeHtml(counts[0].provider)}).</span></div>`,
      `<div class="insight"><strong>${number(unlimited.length)} offres illimitées</strong><span>${number(unlimitedShare)} % du catalogue. Elles ne sont pas assimilées à un volume en Go.</span></div>`,
      `<div class="insight"><strong>${number(destinationCounts.size)} destinations libellées</strong><span>La plus représentée est « ${escapeHtml(topDestination[0])} » (${number(topDestination[1])} offres).</span></div>`
    ].join("");
    const filter = document.getElementById("providerFilter");
    providers.forEach(provider=>filter.add(new Option(provider,provider)));
    const search = document.getElementById("search");
    const pageSize = 50;
    let page = 0;
    function escapeHtml(value){return String(value??"").replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]))}
    function renderTable(){
      const term=search.value.trim().toLocaleLowerCase("fr");
      const chosen=filter.value;
      const filtered=rows.filter(row=>(!chosen||row.provider===chosen)&&(!term||`${row.name} ${row.destination} ${row.provider} ${row.dataLabel}`.toLocaleLowerCase("fr").includes(term)));
      const pages=Math.max(1,Math.ceil(filtered.length/pageSize));
      page=Math.min(page,pages-1);
      document.getElementById("productRows").innerHTML=filtered.slice(page*pageSize,(page+1)*pageSize).map(row=>`<tr><td>${escapeHtml(row.provider)}</td><td title="${escapeHtml(row.name)}">${escapeHtml(row.name)}</td><td>${escapeHtml(row.destination)}</td><td>${escapeHtml(row.dataLabel||"—")}</td><td>${row.validity===null?"—":`${number(row.validity)} jours`}</td><td>${escapeHtml(row.network||"—")}</td><td>${money(row.price)}</td></tr>`).join("")||'<tr><td colspan="7">Aucun produit ne correspond à cette recherche.</td></tr>';
      const start=filtered.length?page*pageSize+1:0;
      document.getElementById("pageLabel").textContent=`${number(start)}–${number(Math.min((page+1)*pageSize,filtered.length))} sur ${number(filtered.length)} offres`;
      document.getElementById("previous").disabled=page===0;
      document.getElementById("next").disabled=page>=pages-1;
    }
    search.addEventListener("input",()=>{page=0;renderTable()});
    filter.addEventListener("change",()=>{page=0;renderTable()});
    document.getElementById("previous").addEventListener("click",()=>{page--;renderTable()});
    document.getElementById("next").addEventListener("click",()=>{page++;renderTable()});
    document.getElementById("source").textContent=`Source : ${providers.length} fichiers CSV · ${number(total)} lignes produits · prix affichés dans la devise des fichiers (EUR).`;
    renderTable();
  </script>
</body>
</html>
"""
    return template.replace("__DATA__", payload)


def main():
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(f"Dossier de données introuvable : {DATA_DIR}")
    files = sorted(DATA_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"Aucun CSV trouvé dans {DATA_DIR}")
    products = []
    for path in files:
        products.extend(read_csv(path))
    dashboard = build_dashboard(products)
    OUTPUT.write_text(dashboard, encoding="utf-8")
    INDEX_OUTPUT.write_text(dashboard, encoding="utf-8")
    print(
        f"Dashboard créé : {OUTPUT} et {INDEX_OUTPUT} "
        f"({len(products)} produits, {len(files)} fichiers)"
    )


if __name__ == "__main__":
    main()
