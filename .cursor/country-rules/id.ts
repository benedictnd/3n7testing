export const IndonesiaGitRules = {
  compliance: {
    data_residency: {
      required: true,
      storage_location: 'jakarta-cdn-01',
      backup_location: 'surabaya-dr-02'
    },
    commit_policy: {
      time_window: '08:00-17:00 WIB',
      holiday_blackouts: ['2024-08-17'], // Indonesian Independence Day
      max_commits_per_hour: 15
    }
  },
  content_filters: {
    exclude_patterns: [
      '/draft-proposals',
      '/experimental-features'
    ]
  }
}; 