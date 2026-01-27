/**
 * CRM Maestro: Loyalty & Health Dashboard Component
 * High-End Visuals for Revenue Tracking
 */

export class LoyaltyCalculator {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
    }

    /**
     * Renders a "Health Ring" visualization
     * @param {number} score - 0 to 100
     */
    renderHealthRing(score) {
        const x = this.canvas.width / 2;
        const y = this.canvas.height / 2;
        const radius = 70;

        // Clear
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Background Ring
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
        this.ctx.strokeStyle = '#f1f1f1';
        this.ctx.lineWidth = 10;
        this.ctx.stroke();

        // Progress Ring (Luxury Gold Gradient)
        const gradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, 0);
        gradient.addColorStop(0, '#D4AF37'); // Gold
        gradient.addColorStop(1, '#FFD700');

        const endAngle = (score / 100) * 2 * Math.PI - (Math.PI / 2);
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, -Math.PI / 2, endAngle);
        this.ctx.strokeStyle = gradient;
        this.ctx.lineCap = 'round';
        this.ctx.stroke();

        // Text
        this.ctx.font = 'bold 24px Inter, sans-serif';
        this.ctx.fillStyle = '#1a1a1a';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(`${score}%`, x, y + 8);
    }

    /**
     * Calculates LTV Projection
     */
    calculateLTV(avgOrderValue, purchaseFrequency, lifespanYears) {
        const ltv = avgOrderValue * purchaseFrequency * lifespanYears;
        console.log(`[CRM Maestro] Projected LTV: $${ltv.toFixed(2)}`);
        return ltv;
    }
}
