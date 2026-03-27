package utils

import (
	"fmt"
	"strings"
)

func AppendTrailingDotIfNotPresent(s *string) {
	if !strings.HasSuffix(*s, ".") {
		*s = fmt.Sprintf("%s%s", *s, ".")
	}
}
