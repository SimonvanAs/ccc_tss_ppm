// TSS PPM v3.0 - Competencies API
import { get } from './client'
import type { Competency, TovLevel } from '../types/competency'

/**
 * Fetch competencies for a specific TOV level.
 */
export async function getCompetencies(tovLevel: TovLevel): Promise<Competency[]> {
  return get<Competency[]>(`/competencies?tov_level=${tovLevel}`)
}
