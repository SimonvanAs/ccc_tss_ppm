// TSS PPM v3.0 - Manager Reassignment API Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { reassignManager } from '../../api/reviews'
import * as client from '../../api/client'

vi.mock('../../api/client', () => ({
  put: vi.fn(),
}))

describe('reassignManager', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should call PUT /reviews/{id}/manager with new_manager_id', async () => {
    const mockResponse = {
      id: 'review-123',
      employee_id: 'emp-456',
      manager_id: 'new-manager-789',
      status: 'DRAFT',
      stage: 'GOAL_SETTING',
      review_year: 2026,
      job_title: 'Software Engineer',
      tov_level: 'B',
    }
    vi.mocked(client.put).mockResolvedValue(mockResponse)

    const result = await reassignManager('review-123', 'new-manager-789')

    expect(client.put).toHaveBeenCalledWith('/reviews/review-123/manager', {
      new_manager_id: 'new-manager-789',
    })
    expect(result).toEqual(mockResponse)
  })

  it('should include optional reason when provided', async () => {
    const mockResponse = {
      id: 'review-123',
      employee_id: 'emp-456',
      manager_id: 'new-manager-789',
      status: 'DRAFT',
      stage: 'GOAL_SETTING',
      review_year: 2026,
      job_title: null,
      tov_level: null,
    }
    vi.mocked(client.put).mockResolvedValue(mockResponse)

    await reassignManager('review-123', 'new-manager-789', 'Manager left the company')

    expect(client.put).toHaveBeenCalledWith('/reviews/review-123/manager', {
      new_manager_id: 'new-manager-789',
      reason: 'Manager left the company',
    })
  })

  it('should propagate API errors', async () => {
    const error = new Error('Forbidden')
    vi.mocked(client.put).mockRejectedValue(error)

    await expect(reassignManager('review-123', 'invalid-id')).rejects.toThrow('Forbidden')
  })
})
