// TSS PPM v3.0 - Team API
import { get } from './client'
import type { TeamMember } from '../types'

/**
 * Fetch all team members for the current manager.
 * @param reviewYear Optional year to filter reviews
 */
export function fetchTeamMembers(reviewYear?: number): Promise<TeamMember[]> {
  const endpoint = reviewYear
    ? `/manager/team?review_year=${reviewYear}`
    : '/manager/team'
  return get<TeamMember[]>(endpoint)
}
