// TSS PPM v3.0 - Team API Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchTeamMembers } from '../api/team'
import * as client from '../api/client'
import { ScoringStatus } from '../types'

// Mock the client module
vi.mock('../api/client', () => ({
  get: vi.fn(),
}))

describe('Team API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchTeamMembers', () => {
    it('should fetch team members for the manager', async () => {
      const mockTeamMembers = [
        {
          id: 'user-1',
          email: 'employee1@example.com',
          first_name: 'John',
          last_name: 'Doe',
          function_title: 'Developer',
          tov_level: 'B',
          review_id: 'review-1',
          review_stage: 'END_YEAR_REVIEW',
          review_status: 'DRAFT',
          scoring_status: ScoringStatus.NOT_STARTED,
        },
        {
          id: 'user-2',
          email: 'employee2@example.com',
          first_name: 'Jane',
          last_name: 'Smith',
          function_title: 'Designer',
          tov_level: 'C',
          review_id: 'review-2',
          review_stage: 'END_YEAR_REVIEW',
          review_status: 'DRAFT',
          scoring_status: ScoringStatus.IN_PROGRESS,
        },
      ]
      vi.mocked(client.get).mockResolvedValueOnce(mockTeamMembers)

      const result = await fetchTeamMembers()

      expect(client.get).toHaveBeenCalledWith('/manager/team')
      expect(result).toEqual(mockTeamMembers)
    })

    it('should fetch team members with review year filter', async () => {
      const mockTeamMembers = [
        {
          id: 'user-1',
          email: 'employee1@example.com',
          first_name: 'John',
          last_name: 'Doe',
          function_title: 'Developer',
          tov_level: 'B',
          review_id: 'review-1',
          review_stage: 'END_YEAR_REVIEW',
          review_status: 'DRAFT',
          scoring_status: ScoringStatus.COMPLETE,
        },
      ]
      vi.mocked(client.get).mockResolvedValueOnce(mockTeamMembers)

      const result = await fetchTeamMembers(2026)

      expect(client.get).toHaveBeenCalledWith('/manager/team?review_year=2026')
      expect(result).toEqual(mockTeamMembers)
    })

    it('should return empty array when no team members', async () => {
      vi.mocked(client.get).mockResolvedValueOnce([])

      const result = await fetchTeamMembers()

      expect(client.get).toHaveBeenCalledWith('/manager/team')
      expect(result).toEqual([])
    })

    it('should handle API errors', async () => {
      vi.mocked(client.get).mockRejectedValueOnce(new Error('Unauthorized'))

      await expect(fetchTeamMembers()).rejects.toThrow('Unauthorized')
    })
  })
})
