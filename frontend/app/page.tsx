"use client";

import { useState } from "react";
import Image from "next/image";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ||
  (typeof window !== "undefined" && window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "");

type AppStatus = "idle" | "generating" | "download_ready" | "error";

export default function Home() {
  const [status, setStatus] = useState<AppStatus>("idle");
  const [materialName, setMaterialName] = useState("");
  const [rawText, setRawText] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [defaultsWarning, setDefaultsWarning] = useState("");

  const extractApiErrorMessage = async (res: Response, fallback: string) => {
    try {
      const payload = await res.json();
      const detail = payload?.detail;

      // Handle FastAPI's detail formats
      if (typeof detail === "string") return detail;
      if (typeof detail === "object" && detail !== null) {
        if (typeof detail.message === "string") return detail.message;
        if (typeof detail[0]?.msg === "string") return `Validation Error: ${detail[0].msg}`;
        return JSON.stringify(detail);
      }
      return fallback;
    } catch {
      return fallback;
    }
  };

  const handleGenerate = async () => {
    if (!materialName.trim() || !rawText.trim()) {
      setErrorMsg("Lütfen hem malzeme adını hem de MatWeb tablo verisini doldurun.");
      setStatus("error");
      return;
    }

    setStatus("generating");
    setErrorMsg("");
    setDefaultsWarning("");

    try {
      const res = await fetch(`${API_BASE}/api/parse-and-generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: materialName, raw_text: rawText }),
      });

      if (!res.ok) {
        const message = await extractApiErrorMessage(res, "XML oluşturma işlemi başarısız oldu.");
        throw new Error(message);
      }

      const defaultsHeader = res.headers.get("X-Mat2Ansys-Used-Defaults") || "";
      const defaults = defaultsHeader
        .split(",")
        .map((x) => x.trim())
        .filter(Boolean);

      if (defaults.length > 0) {
        setDefaultsWarning(
          `Dikkat: MatWeb'de bulunamayan bazı özellikler, standart çelik varsayılanlarıyla dolduruldu (${defaults.join(
            ", "
          )}). Lütfen ANSYS'e aktarmadan önce doğrulayın.`
        );
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      const safeName = materialName.replace(/[^a-zA-Z0-9 _-]/g, "_");
      a.href = url;
      a.download = `${safeName}.xml`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      setStatus("download_ready");
      setTimeout(() => setStatus("idle"), 4000);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Ağ hatası veya bağlantı problemi.";
      setErrorMsg(message);
      setStatus("error");
    }
  };

  return (
    <div className="saas-container">
      <header className="saas-header">
        <div className="brand">
          <div className="logo-box" style={{ overflow: "hidden", position: "relative" }}>
            <Image
              src="/logo.jpg"
              alt="Mat2Ansys Logo"
              fill
              style={{ objectFit: "cover" }}
            />
          </div>
          <div>
            <h1>Mat2Ansys</h1>
            <p>MatWeb - Ansys Köprüsü</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--success)" }}>● Sistem Aktif</span>
        </div>
      </header>

      <main className="saas-grid">

        {/* SOL KOLON: REHBER */}
        <section className="guide-section">
          <div className="saas-card">
            <h2 className="saas-card-title">
              Nasıl Kullanılır?
            </h2>

            <div className="guide-step">
              <div className="step-header">
                <div className="step-number">1</div>
                <div>
                  <h3 className="step-title">MatWeb'de Malzeme Arayın</h3>
                  <p className="step-desc">
                    <a href="https://www.matweb.com/" target="_blank" rel="noopener noreferrer" className="guide-link">
                      matweb.com
                    </a> adresine gidin. Arama çubuğuna aradığınız malzemeyi (Örn: SAE 8620) yazın ve hedef alaşımı seçin.
                  </p>
                </div>
              </div>
              <div className="step-image">
                <Image
                  src="/guide_search.png"
                  alt="MatWeb'de Arama Yapmak"
                  width={600}
                  height={300}
                  style={{ width: "100%", height: "auto" }}
                />
              </div>
            </div>

            <div className="guide-step">
              <div className="step-header">
                <div className="step-number">2</div>
                <div>
                  <h3 className="step-title">"Printer Friendly" Versiyonunu Açın</h3>
                  <p className="step-desc">
                    Malzeme özellik sayfasının sağ üst köşesinde bulunan <strong>Printer Friendly Version</strong> butonuna tıklayın. Açılan temiz sayfadaki tablonun tüm metnini Ctrl+A veya fare ile seçip kopyalayın.
                  </p>
                </div>
              </div>
              <div className="step-image">
                <Image
                  src="/guide_printer.png"
                  alt="Printer Friendly Butonu"
                  width={600}
                  height={300}
                  style={{ width: "100%", height: "auto" }}
                />
              </div>
            </div>

            <div className="guide-step">
              <div className="step-header">
                <div className="step-number">3</div>
                <div>
                  <h3 className="step-title">Veriyi Yapıştırın</h3>
                  <p className="step-desc">
                    Kopyaladığınız içeriği sağdaki <strong>MatWeb Verisi</strong> alanına yapıştırıp "XML Üret ve İndir" butonuna basarak ANSYS dosyanızı alın.
                  </p>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* SAĞ KOLON: FORM */}
        <section className="form-section">
          <div className="saas-card" style={{ position: "sticky", top: "2rem" }}>
            <h2 className="saas-card-title">
              XML Üretici
            </h2>

            {errorMsg && (
              <div className="alert alert-error">
                <strong>Hata:</strong> {errorMsg}
              </div>
            )}

            {defaultsWarning && (
              <div className="alert alert-warning">
                <strong>Bilgi:</strong> {defaultsWarning}
              </div>
            )}

            {status === "download_ready" && (
              <div className="alert alert-success">
                <strong>Başarılı!</strong> XML dosyası indirildi. ANSYS Engineering Data içerisine import edebilirsiniz.
              </div>
            )}

            <div className="form-group">
              <label className="form-label" htmlFor="material-name">Malzeme Adı</label>
              <span className="form-hint">ANSYS içerisinde görünecek referans isim (Örn: SAE 8620 H)</span>
              <input
                id="material-name"
                type="text"
                className="form-input"
                placeholder="Malzeme adı girin..."
                value={materialName}
                onChange={(e) => setMaterialName(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="raw-data">MatWeb Verisi (Smart Paste)</label>
              <span className="form-hint">Printer Friendly Version tablosunun tamamını buraya yapıştırın. Sistem parametreleri otomatik çekecektir.</span>
              <textarea
                id="raw-data"
                className="form-textarea"
                placeholder="Özellikler tablosunu buraya yapıştırın..."
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
              />
            </div>

            <button
              className="btn-primary"
              onClick={handleGenerate}
              disabled={status === "generating"}
            >
              {status === "generating" ? (
                <>
                  <span style={{ marginRight: "10px" }}>⏳</span> Veriler İşleniyor...
                </>
              ) : (
                "Ansys XML Üret ve İndir"
              )}
            </button>

          </div>
        </section>

      </main>
    </div>
  );
}
