import { useState, useEffect } from 'react'
import api from '../../api/client'

/**
 * Import Subjects Modal
 *
 * Allows converting subject images from the subjects directory into character entities.
 * Displays available subjects and creates characters with optional analysis.
 */
function ImportSubjectsModal({ isOpen, onClose, onCharactersImported }) {
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [importing, setImporting] = useState(false)
  const [selectedSubjects, setSelectedSubjects] = useState(new Set())

  useEffect(() => {
    if (isOpen) {
      loadSubjects()
    }
  }, [isOpen])

  const loadSubjects = async () => {
    setLoading(true)
    try {
      const response = await api.get('/analyze/subjects')
      setSubjects(response.data)
    } catch (err) {
      console.error('Failed to load subjects:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleSubject = (filename) => {
    const newSelected = new Set(selectedSubjects)
    if (newSelected.has(filename)) {
      newSelected.delete(filename)
    } else {
      newSelected.add(filename)
    }
    setSelectedSubjects(newSelected)
  }

  const selectAll = () => {
    setSelectedSubjects(new Set(subjects.map(s => s.filename)))
  }

  const deselectAll = () => {
    setSelectedSubjects(new Set())
  }

  const handleImport = async () => {
    if (selectedSubjects.size === 0) return

    setImporting(true)
    const importedCount = []

    for (const filename of selectedSubjects) {
      try {
        // Extract name from filename (remove extension)
        const name = filename.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ')

        // Create character from subject with analysis
        const response = await api.post('/characters/from-subject', {
          subject_path: filename,
          name: name.charAt(0).toUpperCase() + name.slice(1),
          analyze_first: true,
          create_presets: false // Don't create duplicate presets
        })

        importedCount.push(response.data.character.name)
        console.log(`✅ Imported: ${response.data.character.name}`)
      } catch (err) {
        console.error(`Failed to import ${filename}:`, err)
      }
    }

    setImporting(false)

    if (importedCount.length > 0) {
      alert(`Successfully imported ${importedCount.length} character(s):\n${importedCount.join(', ')}`)

      // Reset selection and close
      setSelectedSubjects(new Set())
      if (onCharactersImported) {
        onCharactersImported()
      }
      onClose()
    } else {
      alert('Failed to import any characters')
    }
  }

  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 10000,
        padding: '2rem'
      }}
      onClick={() => !importing && onClose()}
    >
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(30, 30, 40, 0.98) 0%, rgba(20, 20, 30, 0.98) 100%)',
          borderRadius: '16px',
          maxWidth: '800px',
          width: '100%',
          maxHeight: '90vh',
          overflow: 'hidden',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1)',
          display: 'flex',
          flexDirection: 'column'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ padding: '2rem', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <h2 style={{ color: 'white', margin: '0 0 0.5rem 0', fontSize: '1.75rem' }}>
            📸 Import from Subjects
          </h2>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', margin: 0, fontSize: '0.95rem' }}>
            Convert subject images into character entities
          </p>
        </div>

        <div style={{ flex: 1, overflow: 'auto', padding: '2rem' }}>
          {loading ? (
            <div style={{ textAlign: 'center', color: 'rgba(255, 255, 255, 0.7)', padding: '2rem' }}>
              Loading subjects...
            </div>
          ) : subjects.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'rgba(255, 255, 255, 0.7)', padding: '2rem' }}>
              No subject images found in the subjects directory
            </div>
          ) : (
            <>
              <div style={{ marginBottom: '1rem', display: 'flex', gap: '1rem', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                  {selectedSubjects.size} of {subjects.length} selected
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    onClick={selectAll}
                    disabled={importing}
                    style={{
                      padding: '0.5rem 1rem',
                      background: 'rgba(255, 255, 255, 0.1)',
                      color: 'white',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '6px',
                      fontSize: '0.85rem',
                      cursor: importing ? 'not-allowed' : 'pointer',
                      opacity: importing ? 0.5 : 1
                    }}
                  >
                    Select All
                  </button>
                  <button
                    onClick={deselectAll}
                    disabled={importing}
                    style={{
                      padding: '0.5rem 1rem',
                      background: 'rgba(255, 255, 255, 0.1)',
                      color: 'white',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '6px',
                      fontSize: '0.85rem',
                      cursor: importing ? 'not-allowed' : 'pointer',
                      opacity: importing ? 0.5 : 1
                    }}
                  >
                    Deselect All
                  </button>
                </div>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
                gap: '1rem'
              }}>
                {subjects.map(subject => {
                  const isSelected = selectedSubjects.has(subject.filename)
                  const name = subject.filename.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ')

                  return (
                    <div
                      key={subject.filename}
                      onClick={() => !importing && toggleSubject(subject.filename)}
                      style={{
                        background: isSelected
                          ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%)'
                          : 'rgba(255, 255, 255, 0.05)',
                        border: isSelected
                          ? '2px solid rgba(102, 126, 234, 0.6)'
                          : '2px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '12px',
                        padding: '0.75rem',
                        cursor: importing ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s',
                        opacity: importing ? 0.5 : 1
                      }}
                    >
                      <div style={{
                        aspectRatio: '3/4',
                        background: 'rgba(0, 0, 0, 0.3)',
                        borderRadius: '8px',
                        marginBottom: '0.5rem',
                        overflow: 'hidden',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <img
                          src={`/subjects/${subject.filename}`}
                          alt={name}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                          }}
                          onError={(e) => {
                            e.target.style.display = 'none'
                            e.target.parentElement.innerHTML = '<div style="font-size: 2rem">👤</div>'
                          }}
                        />
                      </div>
                      <div style={{
                        color: 'white',
                        fontSize: '0.85rem',
                        textAlign: 'center',
                        fontWeight: 500,
                        textTransform: 'capitalize'
                      }}>
                        {name}
                      </div>
                      {isSelected && (
                        <div style={{
                          marginTop: '0.5rem',
                          textAlign: 'center',
                          color: '#667eea',
                          fontSize: '1.2rem'
                        }}>
                          ✓
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </>
          )}
        </div>

        <div style={{
          padding: '1.5rem 2rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          gap: '1rem',
          justifyContent: 'flex-end'
        }}>
          <button
            onClick={onClose}
            disabled={importing}
            style={{
              padding: '0.75rem 1.5rem',
              background: 'rgba(255, 255, 255, 0.1)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: 500,
              cursor: importing ? 'not-allowed' : 'pointer',
              opacity: importing ? 0.5 : 1
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleImport}
            disabled={importing || selectedSubjects.size === 0}
            style={{
              padding: '0.75rem 1.5rem',
              background: importing || selectedSubjects.size === 0
                ? 'rgba(102, 126, 234, 0.3)'
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: 500,
              cursor: importing || selectedSubjects.size === 0 ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
            }}
          >
            {importing ? 'Importing...' : `Import ${selectedSubjects.size} Character(s)`}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ImportSubjectsModal
