"""
Share code generation utilities using deterministic ID-to-code mapping
Pattern: LLNNN (2 letters + 3 numbers)
Total combinations: 24² × 8³ = 294,912
"""

from app.core.constants import SHARE_CODE_LETTERS, SHARE_CODE_NUMBERS

class ShareCodeGenerator:
    MAX_CODES = 294912  # 24² × 8³
    
    @staticmethod
    def id_to_code(id_: int) -> str:
        """
        Convert database ID to share code using deterministic mapping
        
        Examples:
        1 → AA222
        2 → AA223
        74 → AB222
        294912 → ZZ999
        """
        if id_ < 1 or id_ > ShareCodeGenerator.MAX_CODES:
            raise ValueError(f"ID must be between 1 and {ShareCodeGenerator.MAX_CODES}")
        
        index = id_ - 1  # Start from AA222 (index 0)
        
        # Extract digits (rightmost 3 positions)
        d3 = index % 8
        index //= 8
        d2 = index % 8
        index //= 8
        d1 = index % 8
        index //= 8
        
        # Extract letters (leftmost 2 positions)
        l2 = index % 24
        l1 = index // 24
        
        return f"{SHARE_CODE_LETTERS[l1]}{SHARE_CODE_LETTERS[l2]}{SHARE_CODE_NUMBERS[d1]}{SHARE_CODE_NUMBERS[d2]}{SHARE_CODE_NUMBERS[d3]}"
    
    @staticmethod
    def code_to_id(code: str) -> int:
        """
        Convert share code back to database ID
        
        Examples:
        AA222 → 1
        AA223 → 2
        AB222 → 74
        ZZ999 → 294912
        """
        if len(code) != 5:
            raise ValueError("Share code must be exactly 5 characters")
        
        letters = code[:2]
        numbers = code[2:]
        
        try:
            # Convert letters to indices
            l1_idx = SHARE_CODE_LETTERS.index(letters[0])
            l2_idx = SHARE_CODE_LETTERS.index(letters[1])
            
            # Convert numbers to indices
            d1_idx = SHARE_CODE_NUMBERS.index(numbers[0])
            d2_idx = SHARE_CODE_NUMBERS.index(numbers[1])
            d3_idx = SHARE_CODE_NUMBERS.index(numbers[2])
            
        except ValueError:
            raise ValueError("Invalid characters in share code")
        
        # Reconstruct the index
        index = (l1_idx * 24 + l2_idx) * (8 * 8 * 8) + d1_idx * (8 * 8) + d2_idx * 8 + d3_idx
        
        return index + 1  # Convert back to 1-based ID
    
    @staticmethod
    def is_valid_code(code: str) -> bool:
        """Check if share code format is valid"""
        if len(code) != 5:
            return False
        
        letters = code[:2]
        numbers = code[2:]
        
        # Check if all letters are valid
        for char in letters:
            if char not in SHARE_CODE_LETTERS:
                return False
        
        # Check if all numbers are valid
        for char in numbers:
            if char not in SHARE_CODE_NUMBERS:
                return False
        
        return True
    
    @staticmethod
    def get_next_id_for_overflow(current_max_id: int) -> int:
        """
        Handle overflow by cycling back to beginning
        When we hit MAX_CODES, start from 1 again
        """
        if current_max_id >= ShareCodeGenerator.MAX_CODES:
            return 1  # Start over from the beginning
        return current_max_id + 1

# Global instance
share_code_gen = ShareCodeGenerator()