import request from 'supertest';
import { createApp } from '../src/app.js';

const app = createApp();

describe('Spectra FX API', () => {
  describe('GET /health', () => {
    it('returns service health', async () => {
      const response = await request(app).get('/health');

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        status: 'ok'
      });
      expect(typeof response.body.uptime).toBe('number');
    });
  });

  describe('POST /api/v1/roi', () => {
    it('computes ROI metrics', async () => {
      const payload = {
        volume: 10_000_000,
        spread: 2.5,
        optimization: 0.003
      };

      const response = await request(app).post('/api/v1/roi').send(payload);

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        status: 'success',
        data: {
          monthlySaving: expect.any(Number),
          annualSaving: expect.any(Number),
          roiMultiple: expect.any(Number),
          formatted: {
            monthlySaving: expect.any(String),
            annualSaving: expect.any(String),
            roiMultiple: expect.any(String)
          }
        }
      });
    });

    it('rejects invalid payloads', async () => {
      const response = await request(app).post('/api/v1/roi').send({
        volume: 0,
        spread: -2,
        optimization: 2
      });

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('errors');
    });
  });

  describe('POST /api/v1/contact', () => {
    it('accepts valid lead submissions', async () => {
      const response = await request(app).post('/api/v1/contact').send({
        firstName: 'Alice',
        lastName: 'Martin',
        email: 'alice.martin@example.com',
        company: 'Spectra Capital',
        jobTitle: 'Head of FX',
        monthlyVolume: 30_000_000,
        message: 'Nous souhaitons optimiser nos opérations FX sur les marchés APAC.',
        acceptPrivacyPolicy: true
      });

      expect(response.status).toBe(201);
      expect(response.body).toMatchObject({
        status: 'success',
        data: {
          leadId: expect.any(String)
        }
      });
    });

    it('rejects submissions without privacy consent', async () => {
      const response = await request(app).post('/api/v1/contact').send({
        firstName: 'Alice',
        lastName: 'Martin',
        email: 'alice.martin@example.com',
        company: 'Spectra Capital',
        jobTitle: 'Head of FX',
        monthlyVolume: 30_000_000,
        message: 'Test',
        acceptPrivacyPolicy: false
      });

      expect(response.status).toBe(400);
    });
  });
});
