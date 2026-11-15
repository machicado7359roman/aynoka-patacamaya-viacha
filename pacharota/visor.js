let currentFaces = [];
    let rotY = 0.45, rotX = 0.24, dragging = false, lastX = 0, lastY = 0;

    function hexToRgb(hex) {
      const clean = (hex || "#38bdf8").replace("#", "");
      const num = parseInt(clean, 16);
      return { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
    }

    function update3DModel(cropId) {
      const f = RUDY_MAP[cropId] || RUDY_MAP["quinua_altiplano"];
      const rings = 22, slices = 18;
      const grid = [];
      for (let i = 0; i <= rings; i++) {
        const u = i / rings;
        const row = [];
        for (let j = 0; j < slices; j++) {
          const v = (j / slices) * Math.PI * 2;
          let x = 0, y = (0.5 - u) * 135, z = 0, col = f.color_primario;
          if (f.forma_3d === "panoja_quinua") {
            const r = Math.max(5, 44 * Math.sin(u * Math.PI) * (1 + 0.26 * Math.sin(u * 25) * Math.cos(v * 5)));
            x = Math.cos(v) * r; z = Math.sin(v) * r;
            col = (i + j) % 3 === 0 ? f.color_secundario : f.color_primario;
          } else if (f.forma_3d === "vaina_leguminosa") {
            const bump = 1 + 0.24 * Math.pow(Math.sin(u * Math.PI * 4), 2);
            const r = 25 * Math.sin(u * Math.PI) * bump;
            x = Math.sin(u * Math.PI) * 15 + Math.cos(v) * r;
            z = Math.sin(v) * (r * 0.65);
          } else if (f.forma_3d === "tuberculo_oca") {
            const r = 31 * Math.pow(Math.sin(u * Math.PI), 0.65) * (1 + 0.22 * Math.sin(u * Math.PI * 8));
            x = Math.cos(v) * r; z = Math.sin(v) * r;
            col = Math.sin(u * Math.PI * 8) < -0.5 ? f.color_secundario : f.color_primario;
          } else if (f.forma_3d === "bulbo_raiz") {
            const r = 36 * Math.pow(1 - u, 0.55) * Math.sin(u * Math.PI);
            x = Math.cos(v) * r; z = Math.sin(v) * r;
            col = u < 0.22 ? f.color_secundario : f.color_primario;
          } else if (f.forma_3d === "baya_fruta") {
            const phi = u * Math.PI;
            const heart = 42 * Math.sin(phi) * (1 - 0.25 * Math.cos(phi)) * (1 + 0.08 * Math.sin(u * 30) * Math.cos(v * 8));
            x = Math.cos(v) * heart;
            y = Math.cos(phi) * 46;
            z = Math.sin(v) * heart;
            col = (i + j) % 4 === 0 ? f.color_secundario : f.color_primario;
          } else {
            const phi = u * Math.PI;
            const r = 48 * (1 + 0.12 * Math.sin(phi * 3) * Math.cos(v * 4));
            x = Math.sin(phi) * Math.cos(v) * r;
            y = Math.cos(phi) * 42;
            z = Math.sin(phi) * Math.sin(v) * r;
          }
          row.push({ x, y, z, col });
        }
        grid.push(row);
      }
      currentFaces = [];
      for (let i = 0; i < rings; i++) {
        for (let j = 0; j < slices; j++) {
          const jn = (j + 1) % slices;
          currentFaces.push({
            pts: [grid[i][j], grid[i + 1][j], grid[i + 1][jn], grid[i][jn]],
            rgb: hexToRgb(grid[i][j].col)
          });
        }
      }

    }
    const canvas3d = document.getElementById("farmer-3d-canvas");
    const ctx3d = canvas3d.getContext("2d");
    canvas3d.addEventListener("pointerdown", (e) => { dragging = true; lastX = e.clientX; lastY = e.clientY; });
    window.addEventListener("pointerup", () => { dragging = false; });
    canvas3d.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      rotY += (e.clientX - lastX) * 0.012;
      rotX = Math.max(-1, Math.min(1, rotX + (e.clientY - lastY) * 0.012));
      lastX = e.clientX; lastY = e.clientY;
    });

    function loop3D() {
      const w = canvas3d.clientWidth || 320;
      const h = canvas3d.clientHeight || 275;
      if (canvas3d.width !== w || canvas3d.height !== h) {
        canvas3d.width = w; canvas3d.height = h;
      }
      ctx3d.clearRect(0, 0, w, h);
      if (!dragging) rotY += 0.01;

      const cx = w / 2, cy = h / 2;
      const cy1 = Math.cos(rotY), sy1 = Math.sin(rotY);
      const cx1 = Math.cos(rotX), sx1 = Math.sin(rotX);

      const projected = currentFaces.map((f) => {
        const pts = f.pts.map((p) => {
          const x1 = p.x * cy1 - p.z * sy1;
          const z1 = p.z * cy1 + p.x * sy1;
          const y2 = p.y * cx1 - z1 * sx1;
          const z2 = z1 * cx1 + p.y * sx1;
          const sc = 290 / (290 + z2 + 95);
          return { sx: cx + x1 * sc, sy: cy + y2 * sc, z: z2 };
        });
        const avgZ = (pts[0].z + pts[1].z + pts[2].z + pts[3].z) * 0.25;
        const light = Math.max(0.35, Math.min(1.15, (105 - avgZ) / 145));
        const r = Math.min(255, Math.round(f.rgb.r * light));
        const g = Math.min(255, Math.round(f.rgb.g * light));
        const b = Math.min(255, Math.round(f.rgb.b * light));
        return { pts, avgZ, fill: `rgb(${r},${g},${b})` };
      });

      projected.sort((a, b) => b.avgZ - a.avgZ);
      projected.forEach((d) => {
        ctx3d.beginPath();
        ctx3d.moveTo(d.pts[0].sx, d.pts[0].sy);
        for (let i = 1; i < d.pts.length; i++) ctx3d.lineTo(d.pts[i].sx, d.pts[i].sy);
        ctx3d.closePath();
        ctx3d.fillStyle = d.fill;
        ctx3d.fill();
        ctx3d.strokeStyle = d.fill;
        ctx3d.lineWidth = 0.5;
        ctx3d.stroke();
      });

      requestAnimationFrame(loop3D);
    }
