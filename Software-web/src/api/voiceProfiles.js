import request from '../utils/request'

export const ListVoiceProfilesApi = () => request.get('/voice-profiles')

export const CreateVoiceProfileApi = (formData) => request.post('/voice-profiles', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
  timeout: 120000,
})

export const SetDefaultVoiceProfileApi = (id) => request.post(`/voice-profiles/${id}/default`)

export const DeleteVoiceProfileApi = (id) => request.delete(`/voice-profiles/${id}`)

export const PreviewVoiceProfileApi = (id, text) => request.post(`/voice-profiles/${id}/preview`, { text }, {
  responseType: 'blob',
  timeout: 600000,
})

export const SpeakWithVoiceProfileApi = (data) => request.post('/voice-profiles/speak', data, {
  timeout: 600000,
})
