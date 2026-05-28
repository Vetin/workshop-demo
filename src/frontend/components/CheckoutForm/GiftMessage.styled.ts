// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import styled from 'styled-components';

export const GiftWrapRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
`;

export const GiftMessageTextarea = styled.textarea`
  width: 100%;
  min-height: 80px;
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px solid ${({ theme }) => theme.colors.borderGray};
  border-radius: 4px;
  background: ${({ theme }) => theme.colors.backgroundGray};
  font-size: ${({ theme }) => theme.sizes.mMedium};
  color: ${({ theme }) => theme.colors.textGray};
  resize: vertical;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.otelBlue};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.colors.otelBlue};
  }
`;
