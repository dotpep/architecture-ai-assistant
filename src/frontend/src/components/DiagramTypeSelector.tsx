/**
 * DiagramTypeSelector Component
 * Dropdown for selecting diagram types
 * Requirements: 1.4, 2.4
 */

import React from 'react';
import { DiagramType } from '../types';

interface DiagramTypeSelectorProps {
  selectedType: DiagramType;
  onTypeChange: (type: DiagramType) => void;
  disabled?: boolean;
}

/**
 * Diagram type options with display labels
 */
const DIAGRAM_TYPE_OPTIONS: { value: DiagramType; label: string; description: string }[] = [
  { value: 'flowchart', label: 'Flowchart', description: 'Process flows and workflows' },
  { value: 'erdiagram', label: 'ER Diagram', description: 'Entity relationships' },
  { value: 'sequence', label: 'Sequence', description: 'Interaction sequences' },
  { value: 'class', label: 'Class', description: 'Class structures' },
  { value: 'state', label: 'State', description: 'State machines' },
  { value: 'architecture', label: 'Architecture', description: 'System architecture' },
  { value: 'dfd', label: 'DFD', description: 'Data flow diagrams' },
];

const DiagramTypeSelector: React.FC<DiagramTypeSelectorProps> = ({
  selectedType,
  onTypeChange,
  disabled = false,
}) => {
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onTypeChange(event.target.value as DiagramType);
  };

  const selectedOption = DIAGRAM_TYPE_OPTIONS.find(opt => opt.value === selectedType);

  return (
    <div className="flex flex-col space-y-1">
      <label 
        htmlFor="diagram-type-selector" 
        className="text-sm font-medium text-gray-700"
      >
        Diagram Type
      </label>
      <div className="relative">
        <select
          id="diagram-type-selector"
          value={selectedType}
          onChange={handleChange}
          disabled={disabled}
          className={`
            block w-full pl-3 pr-10 py-2 text-base 
            border border-gray-300 rounded-lg
            focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
            bg-white shadow-sm
            ${disabled ? 'bg-gray-100 cursor-not-allowed opacity-60' : 'cursor-pointer hover:border-gray-400'}
            transition-colors duration-200
          `}
          aria-describedby="diagram-type-description"
        >
          {DIAGRAM_TYPE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {/* Custom dropdown arrow */}
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      {/* Description of selected type */}
      {selectedOption && (
        <p 
          id="diagram-type-description" 
          className="text-xs text-gray-500"
        >
          {selectedOption.description}
        </p>
      )}
    </div>
  );
};

export default DiagramTypeSelector;

/**
 * Export diagram type options for use in other components
 */
export { DIAGRAM_TYPE_OPTIONS };
