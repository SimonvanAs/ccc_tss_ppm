// TSS PPM v3.0 - Competencies API
import { get } from './client'
import type { Competency, TovLevel } from '../types/competency'

/**
 * Fetch competencies for a specific TOV level.
 * @param tovLevel - The TOV level (A, B, C, or D)
 * @param language - Language code for indicators (en, nl, es)
 */
export async function getCompetencies(
  tovLevel: TovLevel,
  language: string = 'en'
): Promise<Competency[]> {
  return get<Competency[]>(`/competencies?tov_level=${tovLevel}&language=${language}`)
}
