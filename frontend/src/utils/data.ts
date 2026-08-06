/**
 * Formatação de datas ISO (vindas da API) para exibição em dd/mm/aaaa.
 *
 * Formata manipulando a própria string, sem construir um `Date` a partir de
 * data pura: `new Date("2026-08-06")` é interpretado como meia-noite UTC, e
 * convertê-lo de volta para o fuso horário local (Brasil, UTC-3) resultaria
 * num dia a menos. Datas com `<input type="date">` (`DateField`/`DateRangeField`)
 * continuam em ISO — esta formatação é só para exibição de texto.
 */
export function formatarData(iso: string | null | undefined): string {
  if (!iso) return "—";
  return iso.slice(0, 10).split("-").reverse().join("/");
}

/** Mesma conversão de `formatarData`, preservando hora:minuto. */
export function formatarDataHora(iso: string | null | undefined): string {
  if (!iso) return "—";
  const data = formatarData(iso);
  const hora = iso.slice(11, 16);
  return hora ? `${data} ${hora}` : data;
}
