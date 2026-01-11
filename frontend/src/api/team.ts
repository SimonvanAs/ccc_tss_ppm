// TSS PPM v3.0 - Team API
import { get } from './client'
import type { TeamMember, TeamMemberGrid } from '../types'

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

/**
 * Fetch team members with their 9-grid position data.
 * @param reviewYear Optional year to filter reviews
 */
export function fetchTeamGrid(reviewYear?: number): Promise<TeamMemberGrid[]> {
  const endpoint = reviewYear
    ? `/manager/team/grid?review_year=${reviewYear}`
    : '/manager/team/grid'
  return get<TeamMemberGrid[]>(endpoint)
}
